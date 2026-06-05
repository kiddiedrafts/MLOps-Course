from __future__ import annotations

from typing import Iterable, List, Tuple

import numpy as np
import pandas as pd
from fastapi import HTTPException, status

from . import config
from .schemas import ListingFeatures, PredictionResponse


def records_to_dataframe(records: Iterable[ListingFeatures]) -> pd.DataFrame:
    """Convert validated API payloads into the exact DataFrame expected by the model."""
    rows = [record.model_dump() for record in records]
    df = pd.DataFrame(rows)

    forbidden = [c for c in config.FORBIDDEN_FIELDS if c in df.columns]
    if forbidden:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Forbidden leakage or audit fields are not allowed.",
                "forbidden_fields": forbidden,
            },
        )

    extra_cols = [c for c in df.columns if c not in config.EXPECTED_FEATURE_COLUMNS]
    if extra_cols:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Unknown fields are not allowed.",
                "unknown_fields": extra_cols,
            },
        )

    missing_cols = [c for c in config.EXPECTED_FEATURE_COLUMNS if c not in df.columns]
    if missing_cols:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Missing required feature fields.",
                "missing_fields": missing_cols,
            },
        )

    return df[config.EXPECTED_FEATURE_COLUMNS]


def _to_model_dataframe(df: pd.DataFrame, model) -> pd.DataFrame:
    """Map API feature names to the column names the HW02 sklearn pipeline expects."""
    model_df = df.rename(columns={"host_is_superhost": "is_superhost"})
    model_cols = model.named_steps["preprocessor"].feature_names_in_
    return model_df[model_cols]


def _positive_scores(model, X: pd.DataFrame) -> Tuple[np.ndarray, bool]:
    """Return positive-class scores and whether they are probabilities."""
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1], True
    if hasattr(model, "decision_function"):
        raw = model.decision_function(X)
        return 1 / (1 + np.exp(-raw)), True
    return model.predict(X).astype(float), False


def predict_records(model, records: List[ListingFeatures]) -> List[PredictionResponse]:
    """Run model prediction and return API responses."""
    df = records_to_dataframe(records)
    X = _to_model_dataframe(df, model)
    scores, has_probability = _positive_scores(model, X)

    responses: List[PredictionResponse] = []
    for score in scores:
        prediction = int(score >= config.PREDICTION_THRESHOLD)
        responses.append(
            PredictionResponse(
                prediction=prediction,
                prediction_label=(
                    config.POSITIVE_LABEL if prediction == 1 else config.NEGATIVE_LABEL
                ),
                probability=float(score) if has_probability else None,
                threshold=config.PREDICTION_THRESHOLD,
            )
        )
    return responses
