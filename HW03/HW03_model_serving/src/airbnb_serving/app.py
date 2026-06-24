from __future__ import annotations

import os
from contextlib import asynccontextmanager

import mlflow
import mlflow.sklearn
from dotenv import load_dotenv
from fastapi import FastAPI

from airbnb_serving.predictor import predict_batch, predict_single
from airbnb_serving.schema import ListingFeatures, PredictionResponse

load_dotenv()

model = None
model_run_id = ""


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, model_run_id

    model_run_id = os.environ["MODEL_RUN_ID"]
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://185.50.38.163:33014")
    username = os.getenv("MLFLOW_TRACKING_USERNAME", "") or os.getenv("MLFLOW_USERNAME", "")
    password = os.getenv("MLFLOW_TRACKING_PASSWORD", "") or os.getenv("MLFLOW_PASSWORD", "")

    os.environ["MLFLOW_TRACKING_USERNAME"] = username
    os.environ["MLFLOW_TRACKING_PASSWORD"] = password
    mlflow.set_tracking_uri(tracking_uri)
    model = mlflow.sklearn.load_model(f"runs:/{model_run_id}/model")

    yield


app = FastAPI(title="Airbnb Listing Demand API", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model_run_id": model_run_id}


@app.post("/predict", response_model=PredictionResponse)
def predict(features: ListingFeatures) -> PredictionResponse:
    return predict_single(features, model, model_run_id)


@app.post("/predict/batch", response_model=list[PredictionResponse])
def predict_batch_endpoint(
    features_list: list[ListingFeatures],
) -> list[PredictionResponse]:
    return predict_batch(features_list, model, model_run_id)
