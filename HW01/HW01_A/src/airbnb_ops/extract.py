from pathlib import Path

import pandas as pd


def read_csv_checked(path: Path) -> pd.DataFrame:
    """Read a CSV file, raising FileNotFoundError if missing."""

    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    return pd.read_csv(path)
