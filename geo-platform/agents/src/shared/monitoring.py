"""
Monitoring and performance tracking for GEO agents.
"""

import time
import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import threading
from functools import wraps

from .models import AgentResponse, AnalysisResult


@dataclass
class PerformanceMetrics:
    """Performance metrics for agent operations."""
    operation_name: str
    duration: float
    success: bool
    timestamp: datetime
    agent_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityMetrics:
    """Quality metrics for agent outputs."""
    agent_name: str
    confidence_score: float
    result_count: int
    validation_passed: bool
    processing_time: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemHealth:
    """System health status."""
    timestamp: datetime
    memory_usage: float
    cpu_usage: float
    active_agents: int
    queue_size: int
    error_rate: float
    average_response_time: float


class AgentMonitor:
    """
    Monitor for agent performance and quality metrics.
    """

    def __init__(self, max_metrics_history: int = 1000):
        self.max_metrics_history = max_metrics_history
        self.performance_metrics: deque = deque(maxlen=max_metrics_history)
        self.quality_metrics: deque = deque(maxlen=max_metrics_history)
        self.error_counts: defaultdict = defaultdict(int)
        self.logger = logging.getLogger("geo.monitoring")
        self._lock = threading.Lock()

        # Health check intervals
        self.health_check_interval = 60  # seconds
        self.last_health_check = datetime.now()

    def record_performance(self, operation_name: str, duration: float, success: bool,
                          agent_name: Optional[str] = None, **metadata):
        """Record performance metrics for an operation."""
        metric = PerformanceMetrics(
            operation_name=operation_name,
            duration=duration,
            success=success,
            timestamp=datetime.now(),
            agent_name=agent_name,
            metadata=metadata
        )

        with self._lock:
            self.performance_metrics.append(metric)

        if not success:
            self.error_counts[f"{agent_name}:{operation_name}"] += 1

        self.logger.info(
            f"Performance: {operation_name} - Duration: {duration:.2f}s - "
            f"Success: {success} - Agent: {agent_name}"
        )

    def record_quality(self, agent_response: AgentResponse, validation_passed: bool = True, **metadata):
        """Record quality metrics for an agent response."""
        metric = QualityMetrics(
            agent_name=agent_response.agent_name,
            confidence_score=agent_response.confidence,
            result_count=len(agent_response.results),
            validation_passed=validation_passed,
            processing_time=agent_response.processing_time,
            timestamp=agent_response.timestamp,
            metadata=metadata
        )

        with self._lock:
            self.quality_metrics.append(metric)

        self.logger.info(
            f"Quality: {agent_response.agent_name} - Confidence: {agent_response.confidence:.2f} - "
            f"Results: {len(agent_response.results)} - Validation: {validation_passed}"
        )

    def get_performance_summary(self, agent_name: Optional[str] = None,
                               hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with self._lock:
            relevant_metrics = [
                m for m in self.performance_metrics
                if m.timestamp >= cutoff_time and (agent_name is None or m.agent_name == agent_name)
            ]

        if not relevant_metrics:
            return {"message": "No metrics found for the specified period"}

        total_operations = len(relevant_metrics)
        successful_operations = sum(1 for m in relevant_metrics if m.success)
        failed_operations = total_operations - successful_operations

        durations = [m.duration for m in relevant_metrics]
        avg_duration = sum(durations) / len(durations)

        return {
            "period_hours": hours,
            "agent_name": agent_name,
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "success_rate": successful_operations / total_operations,
            "average_duration": avg_duration,
            "min_duration": min(durations),
            "max_duration": max(durations),
            "error_rate": failed_operations / total_operations
        }

    def get_quality_summary(self, agent_name: Optional[str] = None,
                           hours: int = 24) -> Dict[str, Any]:
        """Get quality summary for the specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with self._lock:
            relevant_metrics = [
                m for m in self.quality_metrics
                if m.timestamp >= cutoff_time and (agent_name is None or m.agent_name == agent_name)
            ]

        if not relevant_metrics:
            return {"message": "No quality metrics found for the specified period"}

        confidence_scores = [m.confidence_score for m in relevant_metrics]
        result_counts = [m.result_count for m in relevant_metrics]
        validation_passed = sum(1 for m in relevant_metrics if m.validation_passed)

        return {
            "period_hours": hours,
            "agent_name": agent_name,
            "total_responses": len(relevant_metrics),
            "average_confidence": sum(confidence_scores) / len(confidence_scores),
            "min_confidence": min(confidence_scores),
            "max_confidence": max(confidence_scores),
            "average_results_per_response": sum(result_counts) / len(result_counts),
            "validation_success_rate": validation_passed / len(relevant_metrics)
        }

    def get_agent_rankings(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get agent performance rankings."""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with self._lock:
            recent_quality = [
                m for m in self.quality_metrics
                if m.timestamp >= cutoff_time
            ]
            recent_performance = [
                m for m in self.performance_metrics
                if m.timestamp >= cutoff_time and m.agent_name
            ]

        agent_stats = defaultdict(lambda: {
            "confidence_scores": [],
            "processing_times": [],
            "success_count": 0,
            "total_operations": 0,
            "validation_passed": 0,
            "total_validations": 0
        })

        # Aggregate quality metrics
        for metric in recent_quality:
            stats = agent_stats[metric.agent_name]
            stats["confidence_scores"].append(metric.confidence_score)
            stats["processing_times"].append(metric.processing_time)
            stats["total_validations"] += 1
            if metric.validation_passed:
                stats["validation_passed"] += 1

        # Aggregate performance metrics
        for metric in recent_performance:
            stats = agent_stats[metric.agent_name]
            stats["total_operations"] += 1
            if metric.success:
                stats["success_count"] += 1

        # Calculate rankings
        rankings = []
        for agent_name, stats in agent_stats.items():
            if stats["confidence_scores"]:
                avg_confidence = sum(stats["confidence_scores"]) / len(stats["confidence_scores"])
                avg_processing_time = sum(stats["processing_times"]) / len(stats["processing_times"])
                success_rate = stats["success_count"] / max(stats["total_operations"], 1)
                validation_rate = stats["validation_passed"] / max(stats["total_validations"], 1)

                # Calculate composite score (higher is better)
                composite_score = (
                    avg_confidence * 0.3 +
                    success_rate * 0.3 +
                    validation_rate * 0.2 +
                    (1 / max(avg_processing_time, 0.1)) * 0.2  # Inverse of processing time
                )

                rankings.append({
                    "agent_name": agent_name,
                    "composite_score": composite_score,
                    "average_confidence": avg_confidence,
                    "success_rate": success_rate,
                    "validation_rate": validation_rate,
                    "average_processing_time": avg_processing_time,
                    "total_operations": stats["total_operations"]
                })

        return sorted(rankings, key=lambda x: x["composite_score"], reverse=True)

    def get_system_health(self) -> SystemHealth:
        """Get current system health status."""
        try:
            import psutil
            memory_usage = psutil.virtual_memory().percent
            cpu_usage = psutil.cpu_percent()
        except ImportError:
            memory_usage = 0.0
            cpu_usage = 0.0

        # Calculate error rate from recent metrics
        recent_performance = [
            m for m in self.performance_metrics
            if m.timestamp >= datetime.now() - timedelta(minutes=10)
        ]

        if recent_performance:
            error_rate = sum(1 for m in recent_performance if not m.success) / len(recent_performance)
            avg_response_time = sum(m.duration for m in recent_performance) / len(recent_performance)
        else:
            error_rate = 0.0
            avg_response_time = 0.0

        # Count active agents
        active_agents = len(set(
            m.agent_name for m in recent_performance
            if m.agent_name and m.timestamp >= datetime.now() - timedelta(minutes=5)
        ))

        return SystemHealth(
            timestamp=datetime.now(),
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            active_agents=active_agents,
            queue_size=0,  # Would need queue integration
            error_rate=error_rate,
            average_response_time=avg_response_time
        )

    def export_metrics(self, filepath: str, hours: int = 24):
        """Export metrics to JSON file."""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with self._lock:
            performance_data = [
                {
                    "operation_name": m.operation_name,
                    "duration": m.duration,
                    "success": m.success,
                    "timestamp": m.timestamp.isoformat(),
                    "agent_name": m.agent_name,
                    "metadata": m.metadata
                }
                for m in self.performance_metrics if m.timestamp >= cutoff_time
            ]

            quality_data = [
                {
                    "agent_name": m.agent_name,
                    "confidence_score": m.confidence_score,
                    "result_count": m.result_count,
                    "validation_passed": m.validation_passed,
                    "processing_time": m.processing_time,
                    "timestamp": m.timestamp.isoformat(),
                    "metadata": m.metadata
                }
                for m in self.quality_metrics if m.timestamp >= cutoff_time
            ]

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "period_hours": hours,
            "performance_metrics": performance_data,
            "quality_metrics": quality_data,
            "system_health": self.get_system_health().__dict__
        }

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)

        self.logger.info(f"Metrics exported to {filepath}")


# Global monitor instance
monitor = AgentMonitor()


def performance_monitor(operation_name: str = None):
    """
    Decorator to monitor function performance.

    Args:
        operation_name: Name of the operation (defaults to function name)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            agent_name = None

            # Try to extract agent name from self
            if args and hasattr(args[0], 'name'):
                agent_name = args[0].name

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                op_name = operation_name or func.__name__
                monitor.record_performance(op_name, duration, success, agent_name)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            agent_name = None

            # Try to extract agent name from self
            if args and hasattr(args[0], 'name'):
                agent_name = args[0].name

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                op_name = operation_name or func.__name__
                monitor.record_performance(op_name, duration, success, agent_name)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def quality_monitor(func: Callable):
    """
    Decorator to monitor agent response quality.
    Should be used on methods that return AgentResponse.
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        if isinstance(result, AgentResponse):
            monitor.record_quality(result)
        return result

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, AgentResponse):
            monitor.record_quality(result)
        return result

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


class HealthChecker:
    """
    Health checker for continuous monitoring.
    """

    def __init__(self, monitor: AgentMonitor, check_interval: int = 60):
        self.monitor = monitor
        self.check_interval = check_interval
        self.running = False
        self.logger = logging.getLogger("geo.health")

    async def start_monitoring(self):
        """Start continuous health monitoring."""
        self.running = True
        self.logger.info("Health monitoring started")

        while self.running:
            try:
                health = self.monitor.get_system_health()

                # Log health status
                self.logger.info(
                    f"System Health - Memory: {health.memory_usage:.1f}% - "
                    f"CPU: {health.cpu_usage:.1f}% - Active Agents: {health.active_agents} - "
                    f"Error Rate: {health.error_rate:.2f} - Avg Response: {health.average_response_time:.2f}s"
                )

                # Check for alerts
                self._check_alerts(health)

                await asyncio.sleep(self.check_interval)

            except Exception as e:
                self.logger.error(f"Health check error: {e}")
                await asyncio.sleep(self.check_interval)

    def stop_monitoring(self):
        """Stop health monitoring."""
        self.running = False
        self.logger.info("Health monitoring stopped")

    def _check_alerts(self, health: SystemHealth):
        """Check for alert conditions."""
        alerts = []

        if health.memory_usage > 90:
            alerts.append(f"High memory usage: {health.memory_usage:.1f}%")

        if health.cpu_usage > 90:
            alerts.append(f"High CPU usage: {health.cpu_usage:.1f}%")

        if health.error_rate > 0.1:  # 10% error rate
            alerts.append(f"High error rate: {health.error_rate:.2%}")

        if health.average_response_time > 30:  # 30 seconds
            alerts.append(f"Slow response times: {health.average_response_time:.2f}s")

        if health.active_agents == 0:
            alerts.append("No active agents detected")

        for alert in alerts:
            self.logger.warning(f"ALERT: {alert}")


# Initialize health checker
health_checker = HealthChecker(monitor)