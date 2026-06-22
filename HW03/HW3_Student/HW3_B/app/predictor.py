"""app.predictor — thin wrapper over the bundle's BundlePredictor."""
from __future__ import annotations

from typing import List, Sequence

import numpy as np

from . import config


def embed_texts(predictor, texts: Sequence[str]) -> np.ndarray:
    if not texts:
        return np.zeros((0, config.EMBED_DIM), dtype=np.float32)
    arr = predictor.embed(list(texts))
    if arr.shape[1] != config.EMBED_DIM:
        raise ValueError(f"expected dim {config.EMBED_DIM}, got {arr.shape[1]}")
    return arr.astype(np.float32, copy=False)


def cosine(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a_n = a / np.linalg.norm(a, axis=1, keepdims=True).clip(min=1e-9)
    b_n = b / np.linalg.norm(b, axis=1, keepdims=True).clip(min=1e-9)
    return a_n @ b_n.T
