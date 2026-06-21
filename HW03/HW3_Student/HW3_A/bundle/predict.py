#!/usr/bin/env python
"""predict.py — Self-contained embedding inference."""
from __future__ import annotations

import os
import numpy as np
from pathlib import Path
from typing import List, Tuple

import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

BUNDLE_DIR = os.getenv("BUNDLE_DIR", os.path.join(os.path.dirname(__file__), "model"))
MAX_SEQ_LEN = 256
EMBEDDING_DIM = 384
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model = None
_tokenizer = None
_device: torch.device | None = None
_bundle_dir: str | None = None


def _get_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_bundle(bundle_dir: str | None = None) -> Tuple:
    global _model, _tokenizer, _device, _bundle_dir

    path = bundle_dir or BUNDLE_DIR
    _bundle_dir = str(Path(path).resolve())

    torch.manual_seed(0)
    _device = _get_device()

    _tokenizer = AutoTokenizer.from_pretrained(_bundle_dir)
    _model = AutoModel.from_pretrained(_bundle_dir)
    _model.eval()
    _model.to(_device)

    return _model, _tokenizer


def embed(texts: List[str]) -> np.ndarray:
    if not texts:
        return np.zeros((0, EMBEDDING_DIM), dtype=np.float32)

    global _model, _tokenizer, _device
    if _model is None or _tokenizer is None:
        load_bundle()

    encoded = _tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=MAX_SEQ_LEN,
        return_tensors="pt",
    )
    encoded = {k: v.to(_device) for k, v in encoded.items()}

    with torch.no_grad():
        outputs = _model(**encoded)
        last_hidden = outputs.last_hidden_state

    mask = encoded["attention_mask"].unsqueeze(-1).float()
    summed = (last_hidden * mask).sum(dim=1)
    counts = mask.sum(dim=1).clamp(min=1e-9)
    pooled = summed / counts
    normalized = F.normalize(pooled, p=2, dim=1)

    return normalized.detach().cpu().numpy().astype(np.float32)


def similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))


def info() -> dict:
    global _model, _device, _bundle_dir
    if _model is None:
        load_bundle()

    return {
        "model_name": MODEL_NAME,
        "embedding_dim": EMBEDDING_DIM,
        "max_seq_len": MAX_SEQ_LEN,
        "device": _device.type if _device is not None else "cpu",
        "framework": "pytorch",
        "deterministic": True,
        "bundle_dir": _bundle_dir,
    }


if __name__ == "__main__":
    import argparse
    import json
    import sys

    p = argparse.ArgumentParser(description="Bundle embed CLI")
    p.add_argument("--text", action="append", default=[], help="repeatable text input")
    p.add_argument("--texts-file", help="JSON list of strings")
    p.add_argument("--out", help="optional .npy output path")
    p.add_argument("--info", action="store_true", help="print info and exit")
    args = p.parse_args()

    if args.info:
        print(json.dumps(info(), indent=2, default=str))
        raise SystemExit(0)

    texts: list[str] = list(args.text)
    if args.texts_file:
        with open(args.texts_file, encoding="utf-8") as f:
            texts.extend(json.load(f))

    if not texts:
        print("ERROR: provide --text or --texts-file", file=sys.stderr)
        raise SystemExit(2)

    emb = embed(texts)
    if args.out:
        np.save(args.out, emb)
        print(f"Saved {emb.shape} to {args.out}")
    else:
        print(json.dumps([[round(float(x), 6) for x in row] for row in emb]))
