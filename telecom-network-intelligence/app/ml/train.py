"""Training pipeline for telecom quality classification."""

from __future__ import annotations

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from app.ml.preprocess import FEATURE_COLUMNS, prepare_features


def train_models(dataset: pd.DataFrame, model_dir: str = "./models") -> dict[str, object]:
    """Train a lightweight baseline quality classifier and persist it."""
    frame = dataset.copy()
    if "network_quality" not in frame.columns:
        raise ValueError("Dataset must contain 'network_quality' labels for supervised training.")

    features = prepare_features(frame[FEATURE_COLUMNS])
    target = frame["network_quality"]

    if target.nunique() < 2:
        raise ValueError("Training data must include at least two classes for classification.")

    split_kwargs: dict[str, object] = {"test_size": 0.2, "random_state": 42}
    if target.value_counts().min() >= 2:
        split_kwargs["stratify"] = target

    X_train, X_test, y_train, y_test = train_test_split(
        features,
        target,
        **split_kwargs,
    )

    logistic_model = LogisticRegression(max_iter=1000, multi_class="auto")
    logistic_model.fit(X_train, y_train)

    rf_model = RandomForestClassifier(n_estimators=200, random_state=42)
    rf_model.fit(X_train, y_train)

    for model_name, model in {"logistic_regression": logistic_model, "random_forest": rf_model}.items():
        joblib.dump(model, f"{model_dir}/{model_name}.joblib")

    predictions = rf_model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions, output_dict=True)

    return {
        "status": "training_complete",
        "accuracy": round(float(accuracy), 4),
        "report": report,
        "models": ["logistic_regression", "random_forest"],
    }
