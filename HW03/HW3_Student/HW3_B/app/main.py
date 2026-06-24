"""app.main — FastAPI entrypoint for HW3_B."""
from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response, status

from . import client_pg, client_qdrant, config
from . import predictor as predictor_mod
from .model_loader import ModelService
from .schemas import (
    EmbedRequest,
    EmbedResponse,
    HealthResponse,
    ModelInfoResponse,
    PredictRequest,
    PredictResponse,
    RootResponse,
    SearchRequest,
    SearchResponse,
)
from .search import hybrid_search

log = logging.getLogger("hw3_b")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())

model_service = ModelService()
model_service.load()  # eager load for pytest TestClient without lifespan context


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.loaded = False
    log.info("HW3_B starting. BUNDLE_DIR=%s", config.BUNDLE_DIR)
    if not model_service.state.loaded:
        model_service.load()
    app.state.loaded = model_service.state.loaded
    if app.state.loaded:
        log.info("Bundle loaded: %s", model_service.state.bundle_dir)
    else:
        log.error("Bundle load FAILED: %s", model_service.state.error)
    yield
    app.state.loaded = False
    log.info("HW3_B shutting down.")


app = FastAPI(title=config.APP_TITLE, version=config.APP_VERSION, lifespan=lifespan)


@app.get("/", response_model=RootResponse, tags=["service"])
def root() -> RootResponse:
    return RootResponse(
        message="QBC12 HW3 Encoder API",
        docs="/docs",
        health="/health",
        version=config.APP_VERSION,
    )


@app.get("/healthz/live", tags=["service"])
def healthz_live():
    return {"status": "live"}


@app.get("/version", tags=["service"])
def version():
    return {"image_tag": os.getenv("IMAGE_TAG", "unknown")}


@app.get("/healthz/ready", tags=["service"])
def healthz_ready(response: Response):
    if getattr(app.state, "loaded", False):
        return {"status": "ready", "model_loaded": True}
    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "not_ready", "model_loaded": False}


@app.get("/health", response_model=HealthResponse, tags=["service"])
def health() -> HealthResponse:
    bundle_ok = model_service.state.loaded
    qdrant_ok = client_qdrant.ping()
    pg_ok = client_pg.ping()

    if bundle_ok and qdrant_ok and pg_ok:
        status_value = "ok"
    elif bundle_ok:
        status_value = "degraded"
    else:
        status_value = "error"

    return HealthResponse(
        status=status_value,
        bundle_loaded=bundle_ok,
        bundle_dir=str(model_service.state.bundle_dir or ""),
        qdrant_reachable=qdrant_ok,
        pg_reachable=pg_ok,
        error=model_service.state.error,
    )


@app.get("/model-info", response_model=ModelInfoResponse, tags=["model"])
def model_info() -> ModelInfoResponse:
    if not model_service.state.loaded:
        raise HTTPException(status_code=503, detail="model not loaded")

    meta = model_service.metadata
    return ModelInfoResponse(
        bundle_version="1.0.0",
        model_id=meta.get("model_name", "unknown"),
        model_revision=meta.get("model_revision", "unknown"),
        device=config.BUNDLE_DEVICE,
        max_seq_len=int(meta.get("max_seq_len", config.EMBED_MAX_SEQ_LEN)),
        embedding_dim=int(meta.get("embedding_dim", config.EMBED_DIM)),
        bundle_dir=str(model_service.state.bundle_dir or ""),
        qdrant_collection=config.QDRANT_COLLECTION,
        qdrant_vector_count=client_qdrant.vector_count(config.QDRANT_COLLECTION),
        threshold=config.PREDICTION_THRESHOLD,
    )


@app.post("/embed", response_model=EmbedResponse, tags=["embedding"])
def embed(req: EmbedRequest) -> EmbedResponse:
    if not model_service.state.loaded:
        raise HTTPException(status_code=503, detail="model not loaded")
    if len(req.texts) > config.EMBED_BATCH_HARD_CAP:
        raise HTTPException(status_code=413, detail="batch too large")

    t0 = time.perf_counter()
    vectors = predictor_mod.embed_texts(req.texts)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    return EmbedResponse(
        vectors=vectors,
        dim=config.EMBED_DIM,
        count=len(vectors),
        elapsed_ms=elapsed_ms,
    )


@app.post("/predict", response_model=PredictResponse, tags=["embedding"])
def predict(req: PredictRequest) -> PredictResponse:
    if not model_service.state.loaded:
        raise HTTPException(status_code=503, detail="model not loaded")
    if len(req.texts) > config.EMBED_BATCH_HARD_CAP:
        raise HTTPException(status_code=413, detail="batch too large")

    t0 = time.perf_counter()
    vectors = predictor_mod.embed_texts(req.texts)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    return PredictResponse(
        vectors=vectors,
        dim=config.EMBED_DIM,
        count=len(vectors),
        elapsed_ms=elapsed_ms,
    )


@app.post("/search", response_model=SearchResponse, tags=["search"])
def search(req: SearchRequest) -> SearchResponse:
    if not model_service.state.loaded:
        raise HTTPException(status_code=503, detail="model not loaded")
    if len(req.texts) > config.SEARCH_MAX_BATCH_TEXTS:
        raise HTTPException(status_code=413, detail="batch too large")

    t0 = time.perf_counter()
    results = hybrid_search(req.texts, req.top_k, req.filters)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    return SearchResponse(
        results=results,
        count=len(results),
        elapsed_ms=elapsed_ms,
    )


@app.post("/reindex", tags=["admin"])
def reindex():
    if not model_service.state.loaded:
        raise HTTPException(status_code=503, detail="model not loaded")
    from .reindex import run_reindex

    run_reindex()
    return {"status": "ok"}


@app.get("/metrics", tags=["service"])
def metrics():
    return {"status": "ok"}
