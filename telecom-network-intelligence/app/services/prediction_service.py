"""Prediction service layer."""

from __future__ import annotations

from app.ml.predict import predict_quality


class PredictionService:
    """Service wrapper for telecom quality prediction orchestration."""

    def __init__(self) -> None:
        self.name = "PredictionService"

    def predict(self, data, model_path: str = "./models/random_forest.joblib"):
        return predict_quality(data, model_path=model_path)
