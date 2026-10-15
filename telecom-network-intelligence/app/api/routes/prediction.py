"""ML prediction API routes."""

from fastapi import APIRouter, Depends

from app.core.security import require_access_token
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("/quality", response_model=PredictionResponse)
async def predict_quality(
    payload: PredictionRequest,
    _: str = Depends(require_access_token),
) -> PredictionResponse:
    service = PredictionService()
    result = service.predict(
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
    prediction_value = result["prediction"][0]
    confidence_value = result["confidence"][0]
    return PredictionResponse(
        prediction=prediction_value,
        confidence=confidence_value,
        model_version=result["model_version"],
    )


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "prediction service ready"}
