"""
Tests for monitoring system.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from src.shared.monitoring import (
    AgentMonitor, PerformanceMetrics, QualityMetrics, SystemHealth,
    performance_monitor, quality_monitor, HealthChecker
)
from src.shared.models import AgentResponse, AnalysisResult, PriorityLevel, ImpactLevel, EffortLevel, AgentType


class TestAgentMonitor:
    """Test cases for AgentMonitor."""

    @pytest.fixture
    def monitor(self):
        """Create monitor instance."""
        return AgentMonitor(max_metrics_history=100)

    def test_record_performance(self, monitor):
        """Test performance metrics recording."""
        monitor.record_performance("test_operation", 1.5, True, "TestAgent", test_param="value")

        assert len(monitor.performance_metrics) == 1
        metric = monitor.performance_metrics[0]
        assert metric.operation_name == "test_operation"
        assert metric.duration == 1.5
        assert metric.success is True
        assert metric.agent_name == "TestAgent"
        assert metric.metadata["test_param"] == "value"

    def test_record_quality(self, monitor, sample_agent_responses):
        """Test quality metrics recording."""
        response = sample_agent_responses[0]
        monitor.record_quality(response, validation_passed=True, test_param="value")

        assert len(monitor.quality_metrics) == 1
        metric = monitor.quality_metrics[0]
        assert metric.agent_name == response.agent_name
        assert metric.confidence_score == response.confidence
        assert metric.validation_passed is True

    def test_get_performance_summary(self, monitor):
        """Test performance summary generation."""
        # Record some test metrics
        monitor.record_performance("op1", 1.0, True, "Agent1")
        monitor.record_performance("op2", 2.0, False, "Agent1")
        monitor.record_performance("op3", 1.5, True, "Agent2")

        summary = monitor.get_performance_summary(agent_name="Agent1", hours=24)

        assert summary["total_operations"] == 2
        assert summary["successful_operations"] == 1
        assert summary["failed_operations"] == 1
        assert summary["success_rate"] == 0.5
        assert summary["average_duration"] == 1.5

    def test_get_quality_summary(self, monitor, sample_agent_responses):
        """Test quality summary generation."""
        response = sample_agent_responses[0]
        monitor.record_quality(response, validation_passed=True)
        monitor.record_quality(response, validation_passed=False)

        summary = monitor.get_quality_summary(agent_name=response.agent_name, hours=24)

        assert summary["total_responses"] == 2
        assert summary["validation_success_rate"] == 0.5
        assert summary["average_confidence"] == response.confidence

    def test_get_agent_rankings(self, monitor, sample_agent_responses):
        """Test agent rankings generation."""
        for response in sample_agent_responses:
            monitor.record_quality(response, validation_passed=True)
            monitor.record_performance("analyze", response.processing_time, True, response.agent_name)

        rankings = monitor.get_agent_rankings(hours=24)

        assert len(rankings) == len(sample_agent_responses)
        assert all("composite_score" in ranking for ranking in rankings)
        assert all("agent_name" in ranking for ranking in rankings)

        # Rankings should be sorted by composite score (descending)
        for i in range(len(rankings) - 1):
            assert rankings[i]["composite_score"] >= rankings[i + 1]["composite_score"]

    @patch('src.shared.monitoring.psutil')
    def test_get_system_health(self, mock_psutil, monitor):
        """Test system health status."""
        # Mock psutil
        mock_psutil.virtual_memory.return_value.percent = 75.0
        mock_psutil.cpu_percent.return_value = 50.0

        # Add some performance metrics
        monitor.record_performance("test", 1.0, True, "Agent1")
        monitor.record_performance("test", 2.0, False, "Agent2")

        health = monitor.get_system_health()

        assert isinstance(health, SystemHealth)
        assert health.memory_usage == 75.0
        assert health.cpu_usage == 50.0
        assert health.error_rate == 0.5  # 1 failure out of 2 operations
        assert health.active_agents == 2

    def test_export_metrics(self, monitor, sample_agent_responses, tmp_path):
        """Test metrics export."""
        # Record some test data
        response = sample_agent_responses[0]
        monitor.record_quality(response)
        monitor.record_performance("test", 1.0, True, response.agent_name)

        export_file = tmp_path / "metrics.json"
        monitor.export_metrics(str(export_file), hours=24)

        assert export_file.exists()

        import json
        with open(export_file) as f:
            data = json.load(f)

        assert "export_timestamp" in data
        assert "performance_metrics" in data
        assert "quality_metrics" in data
        assert "system_health" in data


class TestPerformanceMonitor:
    """Test cases for performance monitoring decorator."""

    @pytest.fixture
    def test_monitor(self):
        """Create test monitor."""
        return AgentMonitor(max_metrics_history=10)

    @performance_monitor("test_sync")
    def sync_function(self, duration=0.1):
        """Test synchronous function."""
        import time
        time.sleep(duration)
        return "success"

    @performance_monitor("test_async")
    async def async_function(self, duration=0.1):
        """Test asynchronous function."""
        import asyncio
        await asyncio.sleep(duration)
        return "success"

    @performance_monitor("test_error")
    def error_function(self):
        """Test function that raises error."""
        raise ValueError("Test error")

    def test_sync_performance_monitor(self, test_monitor):
        """Test performance monitoring on sync function."""
        with patch('src.shared.monitoring.monitor', test_monitor):
            result = self.sync_function(duration=0.01)

        assert result == "success"
        assert len(test_monitor.performance_metrics) == 1

        metric = test_monitor.performance_metrics[0]
        assert metric.operation_name == "test_sync"
        assert metric.success is True
        assert metric.duration > 0

    @pytest.mark.asyncio
    async def test_async_performance_monitor(self, test_monitor):
        """Test performance monitoring on async function."""
        with patch('src.shared.monitoring.monitor', test_monitor):
            result = await self.async_function(duration=0.01)

        assert result == "success"
        assert len(test_monitor.performance_metrics) == 1

        metric = test_monitor.performance_metrics[0]
        assert metric.operation_name == "test_async"
        assert metric.success is True

    def test_error_performance_monitor(self, test_monitor):
        """Test performance monitoring with errors."""
        with patch('src.shared.monitoring.monitor', test_monitor):
            with pytest.raises(ValueError):
                self.error_function()

        assert len(test_monitor.performance_metrics) == 1

        metric = test_monitor.performance_metrics[0]
        assert metric.operation_name == "test_error"
        assert metric.success is False


class TestQualityMonitor:
    """Test cases for quality monitoring decorator."""

    @pytest.fixture
    def test_monitor(self):
        """Create test monitor."""
        return AgentMonitor(max_metrics_history=10)

    @quality_monitor
    async def mock_analyze(self, confidence=0.8):
        """Mock analyze function that returns AgentResponse."""
        result = AnalysisResult(
            id="test", type="test", title="Test", description="Test",
            priority=PriorityLevel.MEDIUM, impact=ImpactLevel.MEDIUM, effort=EffortLevel.LOW,
            recommendation="Test", confidence=confidence
        )

        return AgentResponse(
            agent_name="TestAgent",
            agent_type=AgentType.AEO,
            results=[result],
            confidence=confidence,
            processing_time=1.0,
            timestamp=datetime.utcnow()
        )

    @pytest.mark.asyncio
    async def test_quality_monitor(self, test_monitor):
        """Test quality monitoring decorator."""
        with patch('src.shared.monitoring.monitor', test_monitor):
            response = await self.mock_analyze(confidence=0.9)

        assert response.confidence == 0.9
        assert len(test_monitor.quality_metrics) == 1

        metric = test_monitor.quality_metrics[0]
        assert metric.agent_name == "TestAgent"
        assert metric.confidence_score == 0.9


class TestHealthChecker:
    """Test cases for HealthChecker."""

    @pytest.fixture
    def health_checker(self):
        """Create health checker instance."""
        monitor = AgentMonitor(max_metrics_history=10)
        return HealthChecker(monitor, check_interval=1)

    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, health_checker):
        """Test starting and stopping health monitoring."""
        assert not health_checker.running

        # Start monitoring (but stop quickly for test)
        import asyncio
        task = asyncio.create_task(health_checker.start_monitoring())

        # Let it run briefly
        await asyncio.sleep(0.1)

        # Stop monitoring
        health_checker.stop_monitoring()
        await task

        assert not health_checker.running

    def test_check_alerts(self, health_checker):
        """Test alert checking."""
        # Create health with alerts
        health = SystemHealth(
            timestamp=datetime.now(),
            memory_usage=95.0,  # High memory
            cpu_usage=95.0,     # High CPU
            active_agents=0,    # No agents
            queue_size=0,
            error_rate=0.5,     # High error rate
            average_response_time=40.0  # Slow responses
        )

        with patch.object(health_checker.logger, 'warning') as mock_warning:
            health_checker._check_alerts(health)

        # Should have logged multiple alerts
        assert mock_warning.call_count >= 4  # At least 4 alert conditions


class TestMonitoringIntegration:
    """Integration tests for monitoring system."""

    @pytest.mark.asyncio
    async def test_full_monitoring_workflow(self, sample_website_data):
        """Test complete monitoring workflow."""
        monitor = AgentMonitor(max_metrics_history=50)

        # Simulate agent operations
        with patch('src.shared.monitoring.monitor', monitor):

            # Mock agent class
            class MockAgent:
                def __init__(self):
                    self.name = "TestAgent"

                @performance_monitor("analyze")
                @quality_monitor
                async def analyze(self, website_data):
                    result = AnalysisResult(
                        id="test", type="test", title="Test", description="Test",
                        priority=PriorityLevel.HIGH, impact=ImpactLevel.HIGH, effort=EffortLevel.LOW,
                        recommendation="Test", confidence=0.85
                    )

                    return AgentResponse(
                        agent_name=self.name,
                        agent_type=AgentType.AEO,
                        results=[result],
                        confidence=0.85,
                        processing_time=1.5,
                        timestamp=datetime.utcnow()
                    )

            agent = MockAgent()
            response = await agent.analyze(sample_website_data)

        # Verify monitoring captured both performance and quality
        assert len(monitor.performance_metrics) == 1
        assert len(monitor.quality_metrics) == 1

        # Check performance metrics
        perf_metric = monitor.performance_metrics[0]
        assert perf_metric.operation_name == "analyze"
        assert perf_metric.agent_name == "TestAgent"
        assert perf_metric.success is True

        # Check quality metrics
        quality_metric = monitor.quality_metrics[0]
        assert quality_metric.agent_name == "TestAgent"
        assert quality_metric.confidence_score == 0.85

        # Get summaries
        perf_summary = monitor.get_performance_summary(hours=1)
        quality_summary = monitor.get_quality_summary(hours=1)

        assert perf_summary["total_operations"] == 1
        assert perf_summary["success_rate"] == 1.0
        assert quality_summary["total_responses"] == 1
        assert quality_summary["average_confidence"] == 0.85