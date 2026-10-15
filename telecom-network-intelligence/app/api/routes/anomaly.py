"""Anomaly detection API routes."""

from fastapi import APIRouter, Depends

from app.core.security import require_access_token
from app.schemas.anomaly import AnomalyRequest, AnomalyResponse
from app.services.anomaly_service import AnomalyService

router = APIRouter(prefix="/detect", tags=["anomaly"])


@router.post("/anomaly", response_model=list[AnomalyResponse])
async def detect_anomaly(
    payload: AnomalyRequest,
    _: str = Depends(require_access_token),
) -> list[AnomalyResponse]:
    service = AnomalyService()
    result = service.detect(
        [
            {
                "rsrp": payload.rsrp,
                "rsrq": payload.rsrq,
                "rssi": payload.rssi,
                "sinr": payload.sinr,
                "download_speed": payload.download_speed,
                "upload_speed": payload.upload_speed,
                "latency": payload.latency,
                "packet_loss": payload.packet_loss,
                "connected_users": payload.connected_users,
                "call_drop_rate": payload.call_drop_rate,
                "handover_failure_rate": payload.handover_failure_rate,
            }
        ]
    )
    return [AnomalyResponse(**item) for item in result]


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "anomaly service ready"}
