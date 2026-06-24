"""app.model_loader — wraps the HW3_A bundle's predict.py."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

_DEFAULT_BUNDLE_IN_IMAGE = "/app/bundle"
_DEV_BUNDLE = str(
    Path(__file__).resolve().parent.parent.parent / "HW3_A" / "bundle"
)


def _resolve_bundle_dir() -> Path:
    env = os.getenv("BUNDLE_DIR", "").strip()
    if env:
        path = Path(env).resolve()
        if path.exists():
            return path
    for candidate in (Path(_DEFAULT_BUNDLE_IN_IMAGE), Path(_DEV_BUNDLE)):
        if candidate.exists():
            return candidate.resolve()
    raise FileNotFoundError(
        "Bundle not found. Set BUNDLE_DIR or build with HW3_A bundle at ../HW3_A/bundle"
    )


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _verify_manifest(bundle_dir: Path) -> tuple[bool, str]:
    manifest_path = bundle_dir / "MANIFEST.json"
    if not manifest_path.exists():
        return False, "MANIFEST.json missing"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = manifest.get("files", {})
    for rel, expected in files.items():
        if str(expected).startswith("REPLACE"):
            return False, f"placeholder hash for {rel}"
        fpath = bundle_dir / rel
        if not fpath.is_file():
            return False, f"missing file: {rel}"
        if _sha256(fpath) != expected:
            return False, f"hash mismatch: {rel}"
    return True, f"{len(files)} files OK"


class BundlePredictor:
    """Thin wrapper over HW3_A predict.py functions."""

    def __init__(self, bundle_dir: Path) -> None:
        bundle_root = bundle_dir.parent if bundle_dir.name == "model" else bundle_dir
        model_dir = bundle_dir if bundle_dir.name == "model" else bundle_dir / "model"
        if str(bundle_root) not in sys.path:
            sys.path.insert(0, str(bundle_root))
        from predict import embed, load_bundle  # type: ignore  # noqa: E402

        load_bundle(str(model_dir))
        self._embed = embed

    def embed(self, texts: List[str]):
        return self._embed(texts)


@dataclass
class LoadState:
    loaded: bool = False
    error: Optional[str] = None
    bundle_dir: Optional[Path] = None
    manifest_ok: Optional[bool] = None
    manifest_msg: Optional[str] = None


@dataclass
class ModelService:
    state: LoadState = field(default_factory=LoadState)
    predictor: Optional[BundlePredictor] = None
    metadata: dict = field(default_factory=dict)

    def load(self) -> None:
        try:
            bundle_dir = _resolve_bundle_dir()
            ok, msg = _verify_manifest(bundle_dir)
            self.state.manifest_ok = ok
            self.state.manifest_msg = msg
            if not ok:
                raise RuntimeError(msg)

            model_dir = bundle_dir / "model"
            if not model_dir.is_dir():
                raise FileNotFoundError(f"model/ missing under {bundle_dir}")

            self.predictor = BundlePredictor(bundle_dir=model_dir)
            meta_path = bundle_dir / "metadata.json"
            if meta_path.exists():
                self.metadata = json.loads(meta_path.read_text(encoding="utf-8"))

            self.state.loaded = True
            self.state.bundle_dir = bundle_dir
            self.state.error = None
        except Exception as exc:
            self.state.loaded = False
            self.state.error = str(exc)

    def require_predictor(self) -> BundlePredictor:
        if not self.state.loaded or self.predictor is None:
            raise RuntimeError(self.state.error or "model not loaded")
        return self.predictor

    def info(self) -> dict:
        return {
            "bundle_loaded": self.state.loaded,
            "bundle_dir": str(self.state.bundle_dir) if self.state.bundle_dir else "",
            "manifest_ok": self.state.manifest_ok,
            "manifest_msg": self.state.manifest_msg,
            "metadata": self.metadata,
            "error": self.state.error,
        }
