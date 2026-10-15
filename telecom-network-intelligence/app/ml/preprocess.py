"""Preprocessing and dataset utilities for telecom quality modeling."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "rsrp",
    "rsrq",
    "rssi",
    "sinr",
    "download_speed",
    "upload_speed",
    "latency",
    "packet_loss",
    "connected_users",
    "call_drop_rate",
    "handover_failure_rate",
]


def prepare_features(records):
    """Normalize telecom records into a clean numeric feature table."""
    if isinstance(records, pd.DataFrame):
        frame = records.copy()
    elif isinstance(records, dict):
        frame = pd.DataFrame([records])
    else:
        frame = pd.DataFrame(records)

    missing = [column for column in FEATURE_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required feature columns: {missing}")

    cleaned = frame[FEATURE_COLUMNS].copy()
    for column in cleaned.columns:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    cleaned = cleaned.fillna(cleaned.median(numeric_only=True))
    return cleaned


def generate_telecom_dataset(output_path: str | Path | None = None, rows: int = 600) -> pd.DataFrame:
    """Create a realistic synthetic telecom dataset with quality labels."""
    rng = np.random.default_rng(42)
    records: list[dict[str, float | int | str]] = []

    for i in range(rows):
        cell_id = f"CELL_{100 + (i % 25)}"
        region = ["Raipur", "Bhopal", "Nagpur", "Delhi", "Mumbai"][i % 5]
        network_type = ["4G", "5G"][i % 2]

        rsrp = float(rng.normal(-95, 10))
        rsrq = float(rng.normal(-12, 4))
        rssi = float(rng.normal(-75, 8))
        sinr = float(rng.normal(15, 8))
        download_speed = float(rng.normal(50, 25))
        upload_speed = float(rng.normal(15, 9))
        latency = float(rng.normal(30, 18))
        packet_loss = float(rng.normal(2, 3))
        connected_users = int(rng.integers(20, 140))
        call_drop_rate = float(rng.normal(1.5, 1.1))
        handover_failure_rate = float(rng.normal(1.8, 1.5))

        quality_score = (
            (rsrp * -0.4)
            + (rsrq * -0.8)
            + (sinr * 0.6)
            + (download_speed * 0.45)
            + (upload_speed * 0.25)
            - (latency * 0.25)
            - (packet_loss * 2.2)
            - (call_drop_rate * 12)
            - (handover_failure_rate * 8)
        )

        quality = "GOOD" if quality_score > 120 else "AVERAGE" if quality_score > 60 else "POOR"

        record = {
            "cell_id": cell_id,
            "region": region,
            "network_type": network_type,
            "timestamp": pd.Timestamp("2024-01-01") + pd.Timedelta(minutes=i * 15),
            "rsrp": round(float(np.clip(rsrp, -130, -40)), 2),
            "rsrq": round(float(np.clip(rsrq, -20, 0)), 2),
            "rssi": round(float(np.clip(rssi, -110, -20)), 2),
            "sinr": round(float(np.clip(sinr, -20, 40)), 2),
            "download_speed": round(float(np.clip(download_speed, 0, 200)), 2),
            "upload_speed": round(float(np.clip(upload_speed, 0, 80)), 2),
            "latency": round(float(np.clip(latency, 0, 200)), 2),
            "packet_loss": round(float(np.clip(packet_loss, 0, 100)), 2),
            "connected_users": connected_users,
            "call_drop_rate": round(float(np.clip(call_drop_rate, 0, 10)), 2),
            "handover_failure_rate": round(float(np.clip(handover_failure_rate, 0, 12)), 2),
            "network_quality": quality,
        }
        records.append(record)

    df = pd.DataFrame(records)
    if output_path is not None:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_file, index=False)
    return df
