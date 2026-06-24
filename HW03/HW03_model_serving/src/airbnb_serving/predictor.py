from __future__ import annotations

import pandas as pd

from airbnb_serving.schema import FEATURE_COLS, ListingFeatures, PredictionResponse


def _to_dataframe(features_list: list[ListingFeatures]) -> pd.DataFrame:
    df = pd.DataFrame([features.model_dump() for features in features_list])
    for col in ("instant_bookable", "is_superhost"):
        if col in df.columns:
            df[col] = df[col].astype("float")
    return df[FEATURE_COLS]


def predict_single(
    features: ListingFeatures, model, run_id: str
) -> PredictionResponse:
    df = _to_dataframe([features])
    prediction = int(model.predict(df)[0])
    probability = float(model.predict_proba(df)[0][1])
    return PredictionResponse(
        prediction=prediction,
        probability_high_demand=probability,
        model_run_id=run_id,
    )


def predict_batch(
    features_list: list[ListingFeatures], model, run_id: str
) -> list[PredictionResponse]:
    df = _to_dataframe(features_list)
    predictions = model.predict(df)
    probabilities = model.predict_proba(df)[:, 1]
    return [
        PredictionResponse(
            prediction=int(pred),
            probability_high_demand=float(prob),
            model_run_id=run_id,
        )
        for pred, prob in zip(predictions, probabilities)
    ]
