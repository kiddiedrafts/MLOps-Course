"""app.config — environment variable contract for HW3_B."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load HW3_B/.env so `make test` works without `source .env`
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

APP_TITLE = "QBC12 HW03-B Encoder Embedding & Search API"
APP_VERSION = "0.1.0"

BUNDLE_DIR = os.getenv("BUNDLE_DIR", "/app/bundle")
BUNDLE_DEVICE = os.getenv("BUNDLE_DEVICE", "cpu")

QDRANT_URL = os.getenv("QDRANT_URL", "http://qbc12-qdrant:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "qbc12_corpus")

DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_NAME = os.getenv("DATABASE_NAME", "qbc12_hw03_encoder")
DATABASE_API_RO_PASSWORD = os.getenv("DATABASE_API_RO_PASSWORD", "")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://qbc12_hw03_api_ro:{DATABASE_API_RO_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}",
)

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "")
MLFLOW_TRACKING_USERNAME = os.getenv("MLFLOW_TRACKING_USERNAME", "")
MLFLOW_TRACKING_PASSWORD = os.getenv("MLFLOW_TRACKING_PASSWORD", "")

STUDENT_USERNAME = os.getenv(
    "STUDENT_USERNAME",
    os.getenv("MLFLOW_TRACKING_USERNAME", "student_unknown"),
)
MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "")
MODEL_NAME = os.getenv("MODEL_NAME", "")

SEARCH_DEFAULT_TOP_K = 10
SEARCH_MAX_TOP_K = 100
SEARCH_MAX_BATCH_TEXTS = 256

EMBED_MAX_SEQ_LEN = 256
EMBED_BATCH_HARD_CAP = 256
EMBED_DIM = 384
