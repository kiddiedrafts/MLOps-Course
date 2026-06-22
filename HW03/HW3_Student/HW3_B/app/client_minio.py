"""app.client_minio — MinIO client (used only for bundle download in s3 mode)."""
from __future__ import annotations

import os
from pathlib import Path

from . import config


def get_credentials() -> dict:
    prefix = os.getenv("MINIO_PREFIX", f"{config.STUDENT_USERNAME}/")
    return {
        "endpoint": os.getenv("MINIO_ENDPOINT", ""),
        "access_key": os.getenv("MINIO_ACCESS_KEY", ""),
        "secret_key": os.getenv("MINIO_SECRET_KEY", ""),
        "bucket": os.getenv("MINIO_BUCKET", "hw03-bundles"),
        "prefix": prefix,
    }


def download_bundle(target_dir: Path) -> bool:
    try:
        from minio import Minio

        creds = get_credentials()
        client = Minio(
            creds["endpoint"],
            access_key=creds["access_key"],
            secret_key=creds["secret_key"],
            secure=False,
        )
        target_dir.mkdir(parents=True, exist_ok=True)
        prefix = creds["prefix"]
        for obj in client.list_objects(creds["bucket"], prefix=prefix, recursive=True):
            rel = obj.object_name[len(prefix) :]
            if not rel or rel.endswith("/"):
                continue
            dest = target_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            client.fget_object(creds["bucket"], obj.object_name, str(dest))
        return True
    except Exception:
        return False
