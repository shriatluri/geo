"""
FastAPI monitoring dashboard for GEO agents.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import asyncio
from datetime import datetime

from src.shared.monitoring import monitor, health_checker
from src.shared.models import AgentType

app = FastAPI(title="GEO Agent Monitoring", version="1.0.0")


@app.get("/health")
async def get_health():
    """Get system health status."""
    health = monitor.get_system_health()
    return {
        "status": "healthy" if health.error_rate < 0.1 else "unhealthy",
        "timestamp": health.timestamp.isoformat(),
        "memory_usage": health.memory_usage,
        "cpu_usage": health.cpu_usage,
        "active_agents": health.active_agents,
        "error_rate": health.error_rate,
        "average_response_time": health.average_response_time
    }


@app.get("/metrics/performance")
async def get_performance_metrics(
    agent_name: Optional[str] = None,
    hours: int = Query(24, ge=1, le=168)  # 1 hour to 1 week
):
    """Get performance metrics summary."""
    summary = monitor.get_performance_summary(agent_name, hours)
    return summary


@app.get("/metrics/quality")
async def get_quality_metrics(
    agent_name: Optional[str] = None,
    hours: int = Query(24, ge=1, le=168)
):
    """Get quality metrics summary."""
    summary = monitor.get_quality_summary(agent_name, hours)
    return summary


@app.get("/metrics/rankings")
async def get_agent_rankings(hours: int = Query(24, ge=1, le=168)):
    """Get agent performance rankings."""
    rankings = monitor.get_agent_rankings(hours)
    return {"rankings": rankings}


@app.get("/metrics/export")
async def export_metrics(
    hours: int = Query(24, ge=1, le=168),
    format: str = Query("json", regex="^(json)$")
):
    """Export metrics data."""
    if format == "json":
        # Export to temporary file and return data
        import tempfile
        import json

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            monitor.export_metrics(f.name, hours)

        with open(f.name, 'r') as f:
            data = json.load(f)

        return JSONResponse(content=data)

    raise HTTPException(status_code=400, detail="Unsupported format")


@app.get("/agents/status")
async def get_agents_status():
    """Get status of all agents."""
    # This would integrate with actual agent registry
    rankings = monitor.get_agent_rankings(1)  # Last hour

    agents_status = []
    for ranking in rankings:
        agents_status.append({
            "name": ranking["agent_name"],
            "status": "healthy" if ranking["success_rate"] > 0.9 else "degraded",
            "success_rate": ranking["success_rate"],
            "average_confidence": ranking["average_confidence"],
            "average_processing_time": ranking["average_processing_time"],
            "last_seen": datetime.now().isoformat()  # Would be actual last seen
        })

    return {"agents": agents_status}


@app.post("/monitoring/start")
async def start_monitoring():
    """Start health monitoring."""
    if not health_checker.running:
        # Start monitoring in background
        asyncio.create_task(health_checker.start_monitoring())
        return {"message": "Health monitoring started"}
    else:
        return {"message": "Health monitoring already running"}


@app.post("/monitoring/stop")
async def stop_monitoring():
    """Stop health monitoring."""
    if health_checker.running:
        health_checker.stop_monitoring()
        return {"message": "Health monitoring stopped"}
    else:
        return {"message": "Health monitoring not running"}


@app.get("/alerts")
async def get_alerts():
    """Get current system alerts."""
    health = monitor.get_system_health()
    alerts = []

    if health.memory_usage > 90:
        alerts.append({
            "level": "critical",
            "message": f"High memory usage: {health.memory_usage:.1f}%",
            "timestamp": health.timestamp.isoformat()
        })

    if health.cpu_usage > 90:
        alerts.append({
            "level": "critical",
            "message": f"High CPU usage: {health.cpu_usage:.1f}%",
            "timestamp": health.timestamp.isoformat()
        })

    if health.error_rate > 0.1:
        alerts.append({
            "level": "warning",
            "message": f"High error rate: {health.error_rate:.2%}",
            "timestamp": health.timestamp.isoformat()
        })

    if health.average_response_time > 30:
        alerts.append({
            "level": "warning",
            "message": f"Slow response times: {health.average_response_time:.2f}s",
            "timestamp": health.timestamp.isoformat()
        })

    if health.active_agents == 0:
        alerts.append({
            "level": "critical",
            "message": "No active agents detected",
            "timestamp": health.timestamp.isoformat()
        })

    return {"alerts": alerts, "count": len(alerts)}


@app.get("/dashboard")
async def get_dashboard_data():
    """Get comprehensive dashboard data."""
    health = monitor.get_system_health()
    performance = monitor.get_performance_summary(hours=24)
    quality = monitor.get_quality_summary(hours=24)
    rankings = monitor.get_agent_rankings(hours=24)

    return {
        "timestamp": datetime.now().isoformat(),
        "system_health": {
            "status": "healthy" if health.error_rate < 0.1 else "unhealthy",
            "memory_usage": health.memory_usage,
            "cpu_usage": health.cpu_usage,
            "active_agents": health.active_agents,
            "error_rate": health.error_rate,
            "average_response_time": health.average_response_time
        },
        "performance_summary": performance,
        "quality_summary": quality,
        "top_agents": rankings[:5],  # Top 5 agents
        "alerts_count": len((await get_alerts())["alerts"])
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)