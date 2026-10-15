"""Pydantic schemas for predictions."""

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    cell_id: str
    region: str
    network_type: str
    rsrp: float
    rsrq: float
    rssi: float
    sinr: float
    download_speed: float
    upload_speed: float
    latency: float
    packet_loss: float
    connected_users: int
    call_drop_rate: float
    handover_failure_rate: float


class PredictionResponse(BaseModel):
    prediction: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    model_version: str

    model_config = {"protected_namespaces": ()}
