from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Optional, List
from common.database import get_db
from monitoring.models import APILog, AgentLog
from monitoring.metrics import metrics_endpoint
from pydantic import BaseModel

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


class LogStats(BaseModel):
    total_requests: int
    average_duration: float
    success_rate: float
    error_count: int


class EndpointStats(BaseModel):
    endpoint: str
    count: int
    avg_duration: float


class AgentStats(BaseModel):
    agent_type: str
    total_requests: int
    success_count: int
    error_count: int
    avg_duration: float
    total_tokens: int


@router.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return metrics_endpoint()


@router.get("/api-logs/stats", response_model=LogStats)
async def get_api_logs_stats(
    hours: int = Query(24, description="Number of hours to look back"),
    db: Session = Depends(get_db)
):
    """Get API logs statistics"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    total = db.query(func.count(APILog.id)).filter(
        APILog.timestamp >= cutoff_time
    ).scalar()

    avg_duration = db.query(func.avg(APILog.duration)).filter(
        APILog.timestamp >= cutoff_time
    ).scalar() or 0

    success_count = db.query(func.count(APILog.id)).filter(
        and_(
            APILog.timestamp >= cutoff_time,
            APILog.status_code < 400
        )
    ).scalar()

    error_count = db.query(func.count(APILog.id)).filter(
        and_(
            APILog.timestamp >= cutoff_time,
            APILog.status_code >= 400
        )
    ).scalar()

    success_rate = (success_count / total * 100) if total > 0 else 0

    return {
        "total_requests": total,
        "average_duration": round(avg_duration, 3),
        "success_rate": round(success_rate, 2),
        "error_count": error_count
    }


@router.get("/api-logs/endpoints", response_model=List[EndpointStats])
async def get_endpoint_stats(
    hours: int = Query(24, description="Number of hours to look back"),
    limit: int = Query(10, description="Number of top endpoints to return"),
    db: Session = Depends(get_db)
):
    """Get top endpoints by request count"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    results = db.query(
        APILog.endpoint,
        func.count(APILog.id).label('count'),
        func.avg(APILog.duration).label('avg_duration')
    ).filter(
        APILog.timestamp >= cutoff_time
    ).group_by(
        APILog.endpoint
    ).order_by(
        func.count(APILog.id).desc()
    ).limit(limit).all()

    return [
        {
            "endpoint": r.endpoint,
            "count": r.count,
            "avg_duration": round(r.avg_duration, 3)
        }
        for r in results
    ]


@router.get("/agent-logs/stats", response_model=List[AgentStats])
async def get_agent_stats(
    hours: int = Query(24, description="Number of hours to look back"),
    db: Session = Depends(get_db)
):
    """Get AI agent statistics"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    results = db.query(
        AgentLog.agent_type,
        func.count(AgentLog.id).label('total'),
        func.sum(
            func.case((AgentLog.status == 'success', 1), else_=0)
        ).label('success_count'),
        func.sum(
            func.case((AgentLog.status == 'error', 1), else_=0)
        ).label('error_count'),
        func.avg(AgentLog.duration).label('avg_duration'),
        func.sum(AgentLog.tokens_used).label('total_tokens')
    ).filter(
        AgentLog.timestamp >= cutoff_time
    ).group_by(
        AgentLog.agent_type
    ).all()

    return [
        {
            "agent_type": r.agent_type,
            "total_requests": r.total,
            "success_count": r.success_count or 0,
            "error_count": r.error_count or 0,
            "avg_duration": round(r.avg_duration, 3),
            "total_tokens": r.total_tokens or 0
        }
        for r in results
    ]


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "disconnected",
            "error": str(e)
        }
