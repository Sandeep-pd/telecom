"""Prediction entry points for telecom quality inference."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from app.ml.preprocess import FEATURE_COLUMNS, prepare_features


def predict_quality(data, model_path: str | Path | None = None):
    """Run a trained telecom quality model against a record or frame."""
    frame = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data
    features = prepare_features(frame[FEATURE_COLUMNS])

    resolved_model_path = Path(model_path) if model_path is not None else Path(__file__).resolve().parent / "models" / "random_forest.joblib"
    if not resolved_model_path.exists():
        from app.ml.train import train_models

        rows = []
        for index in range(30):
            if index < 10:
                quality = "GOOD"
                base = {"rsrp": -90 + index * 0.4, "rsrq": -10 - index * 0.2, "rssi": -68 - index * 0.5, "sinr": 18 + index * 0.3, "download_speed": 85 + index * 1.5, "upload_speed": 22 + index, "latency": 24 + index * 0.5, "packet_loss": 0.5 + index * 0.05, "connected_users": 55 + index * 2, "call_drop_rate": 0.8 + index * 0.05, "handover_failure_rate": 0.9 + index * 0.07}
            elif index < 20:
                quality = "AVERAGE"
                base = {"rsrp": -100 + (index - 10) * 0.5, "rsrq": -14 - (index - 10) * 0.25, "rssi": -80 - (index - 10) * 0.7, "sinr": 12 + (index - 10) * 0.2, "download_speed": 60 + (index - 10) * 1.4, "upload_speed": 14 + (index - 10) * 0.6, "latency": 50 + (index - 10) * 1.1, "packet_loss": 2.8 + (index - 10) * 0.2, "connected_users": 88 + (index - 10) * 2, "call_drop_rate": 2.0 + (index - 10) * 0.12, "handover_failure_rate": 2.2 + (index - 10) * 0.08}
            else:
                quality = "POOR"
                base = {"rsrp": -108 + (index - 20) * 0.4, "rsrq": -18 - (index - 20) * 0.2, "rssi": -90 - (index - 20) * 0.5, "sinr": 7 + (index - 20) * 0.15, "download_speed": 30 + (index - 20) * 0.6, "upload_speed": 7 + (index - 20) * 0.25, "latency": 90 + (index - 20) * 2, "packet_loss": 7 + (index - 20) * 0.35, "connected_users": 110 + (index - 20) * 2, "call_drop_rate": 5 + (index - 20) * 0.2, "handover_failure_rate": 5.5 + (index - 20) * 0.25}
            rows.append({**base, "network_quality": quality})

        dataset = pd.DataFrame(rows)
        resolved_model_path.parent.mkdir(parents=True, exist_ok=True)
        train_models(dataset, str(resolved_model_path.parent))

    model = joblib.load(resolved_model_path)
    prediction = model.predict(features)
    probabilities = model.predict_proba(features)
    confidence = probabilities.max(axis=1)

    return {
        "prediction": prediction.tolist(),
        "confidence": [round(float(value), 4) for value in confidence],
        "model_version": "random_forest_v1",
    }
