"""Anomaly service layer."""

from __future__ import annotations

from app.ml.anomaly import detect_anomaly


class AnomalyService:
    """Service wrapper for telecom anomaly detection orchestration."""

    def __init__(self) -> None:
        self.name = "AnomalyService"

    def detect(self, data, contamination: float = 0.05):
        return detect_anomaly(data, contamination=contamination)
