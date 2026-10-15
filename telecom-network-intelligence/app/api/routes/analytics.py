"""Analytics API routes."""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import require_access_token
from app.database.connection import get_db
from app.models.network import NetworkMeasurement

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
async def analytics_summary(
    db: Session = Depends(get_db),
    _: str = Depends(require_access_token),
) -> dict[str, object]:
    total_measurements = db.query(NetworkMeasurement).count()
    active_cells = db.query(NetworkMeasurement.cell_id).distinct().count()
    avg_latency = db.query(func.avg(NetworkMeasurement.latency)).scalar() or 0
    avg_packet_loss = db.query(func.avg(NetworkMeasurement.packet_loss)).scalar() or 0
    avg_download_speed = db.query(func.avg(NetworkMeasurement.download_speed)).scalar() or 0

    recent_measurements = (
        db.query(NetworkMeasurement)
        .order_by(NetworkMeasurement.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "status": "ready",
        "metrics": {
            "network_quality_model": "random_forest",
            "anomaly_model": "isolation_forest",
            "coverage": ["latency", "packet_loss", "coverage", "handover_quality"],
        },
        "snapshot": {
            "total_measurements": total_measurements,
            "active_cells": active_cells,
            "average_latency_ms": round(float(avg_latency), 2),
            "average_packet_loss_pct": round(float(avg_packet_loss), 2),
            "average_download_speed_mbps": round(float(avg_download_speed), 2),
        },
        "recent_measurements": [
            {
                "id": item.id,
                "cell_id": item.cell_id,
                "region": item.region,
                "network_type": item.network_type,
                "latency": item.latency,
                "packet_loss": item.packet_loss,
                "download_speed": item.download_speed,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            }
            for item in recent_measurements
        ],
    }


@router.get("/trends")
async def analytics_trends(
    db: Session = Depends(get_db),
    _: str = Depends(require_access_token),
) -> dict[str, object]:
    measurements = (
        db.query(NetworkMeasurement)
        .order_by(NetworkMeasurement.created_at.asc())
        .limit(20)
        .all()
    )

    points = []
    for item in measurements:
        points.append(
            {
                "timestamp": item.created_at.isoformat() if item.created_at else datetime.utcnow().isoformat(),
                "latency": float(item.latency),
                "packet_loss": float(item.packet_loss),
                "download_speed": float(item.download_speed),
                "cell_id": item.cell_id,
            }
        )

    return {
        "status": "ready",
        "points": points,
        "series": ["latency", "packet_loss", "download_speed"],
    }


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "analytics service ready"}
