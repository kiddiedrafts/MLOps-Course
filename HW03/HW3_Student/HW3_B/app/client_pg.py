"""app.client_pg — Postgres read-only client (audit + source of truth)."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, List, Optional

import psycopg
from psycopg.rows import dict_row

from . import config


def ping() -> bool:
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return True
    except Exception:
        return False


@contextmanager
def _connect() -> Iterator[psycopg.Connection]:
    conn = psycopg.connect(config.DATABASE_URL, connect_timeout=5)
    try:
        yield conn
    finally:
        conn.close()


def fetch_corpus_hits(ids: List[str]) -> List[dict]:
    if not ids:
        return []
    with _connect() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT id::text AS id, text, primary_label, labels, lang, source
                FROM core.encoder_corpus
                WHERE id = ANY(%s::uuid[])
                """,
                (ids,),
            )
            rows = {row["id"]: row for row in cur.fetchall()}
    return [rows[i] for i in ids if i in rows]


def count_corpus() -> Optional[int]:
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM core.encoder_corpus")
                row = cur.fetchone()
                return int(row[0]) if row else None
    except Exception:
        return None
