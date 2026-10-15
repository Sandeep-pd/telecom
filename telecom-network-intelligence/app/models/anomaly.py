"""Anomaly model for telecom measurement anomalies."""

from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from app.database.connection import Base


class NetworkAnomaly(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    measurement_id = Column(Integer, nullable=False, index=True)
    is_anomaly = Column(Boolean, nullable=False, default=False)
    anomaly_score = Column(Float, nullable=False)
    severity = Column(String, nullable=False)
    possible_causes = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
