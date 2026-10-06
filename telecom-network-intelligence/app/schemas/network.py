"""Pydantic schemas for telecom network measurements."""

from datetime import datetime

from pydantic import BaseModel, Field


class NetworkMeasurementBase(BaseModel):
    cell_id: str = Field(..., min_length=3, max_length=50)
    region: str = Field(..., min_length=2, max_length=100)
    network_type: str = Field(..., pattern=r"^(4G|5G|LTE|3G)$")
    timestamp: datetime | None = None
    rsrp: float = Field(..., ge=-140, le=-40)
    rsrq: float = Field(..., ge=-20, le=0)
    rssi: float = Field(..., ge=-110, le=-20)
    sinr: float = Field(..., ge=-20, le=40)
    download_speed: float = Field(..., ge=0)
    upload_speed: float = Field(..., ge=0)
    latency: float = Field(..., ge=0)
    packet_loss: float = Field(..., ge=0, le=100)
    connected_users: int = Field(..., ge=0)
    call_drop_rate: float = Field(..., ge=0)
    handover_failure_rate: float = Field(..., ge=0)


class NetworkMeasurementCreate(NetworkMeasurementBase):
    pass


class NetworkMeasurementResponse(NetworkMeasurementBase):
    id: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
