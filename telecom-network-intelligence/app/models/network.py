"""Network measurement SQLAlchemy model."""

from __future__ import annotations

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from app.database.connection import Base


class NetworkMeasurement(Base):
    __tablename__ = "network_measurements"

    id = Column(Integer, primary_key=True, index=True)
    cell_id = Column(String, nullable=False, index=True)
    region = Column(String, nullable=False, index=True)
    network_type = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    rsrp = Column(Float, nullable=False)
    rsrq = Column(Float, nullable=False)
    rssi = Column(Float, nullable=False)
    sinr = Column(Float, nullable=False)
    download_speed = Column(Float, nullable=False)
    upload_speed = Column(Float, nullable=False)
    latency = Column(Float, nullable=False)
    packet_loss = Column(Float, nullable=False)
    connected_users = Column(Integer, nullable=False)
    call_drop_rate = Column(Float, nullable=False)
    handover_failure_rate = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
