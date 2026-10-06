"""Pydantic schemas for anomaly detection responses."""

from pydantic import BaseModel, Field


class AnomalyRequest(BaseModel):
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


class AnomalyResponse(BaseModel):
    is_anomaly: bool
    anomaly_score: float
    severity: str = Field(..., pattern=r"^(LOW|MEDIUM|HIGH|CRITICAL)$")
    possible_causes: list[str]
