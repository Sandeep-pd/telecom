"""Isolation-forest-based anomaly detection for telecom KPI streams."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from app.ml.preprocess import FEATURE_COLUMNS, prepare_features


def detect_anomaly(data, contamination: float = 0.05):
    """Flag abnormal telecom records using an unsupervised isolation forest."""
    frame = pd.DataFrame(data)
    features = prepare_features(frame[FEATURE_COLUMNS])

    model = IsolationForest(contamination=contamination, random_state=42)
    model.fit(features)
    scores = model.decision_function(features)
    flags = model.predict(features)

    anomalies = []
    for idx, flag in enumerate(flags):
        severity = "LOW"
        if flag == -1:
            score = float(abs(scores[idx]))
            if score > 0.25:
                severity = "CRITICAL"
            elif score > 0.15:
                severity = "HIGH"
            elif score > 0.08:
                severity = "MEDIUM"
            anomalies.append(
                {
                    "is_anomaly": True,
                    "anomaly_score": round(score, 4),
                    "severity": severity,
                    "possible_causes": [
                        "traffic spike",
                        "radio interference",
                        "handovers failing",
                        "backhaul congestion",
                    ],
                }
            )
        else:
            anomalies.append(
                {
                    "is_anomaly": False,
                    "anomaly_score": round(float(abs(scores[idx])), 4),
                    "severity": "LOW",
                    "possible_causes": [],
                }
            )

    return anomalies
