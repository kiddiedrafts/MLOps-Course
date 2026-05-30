import hashlib

import pandas as pd


# Columns that contain direct PII and must be dropped completely
DIRECT_PII_COLUMNS = ["host_name"]


def pseudonymize_value(value, salt: str = "qbc12") -> str:
    """Convert a value to a stable hash."""
    
    # Combine salt and value, convert to bytes, then hash
    salted = f"{salt}_{value}"
    return hashlib.sha256(salted.encode()).hexdigest()


def handle_pii(df: pd.DataFrame) -> pd.DataFrame:
    """Remove and pseudonymize PII columns from a DataFrame."""
    
    df = df.copy()

    # Step 1: Drop direct PII columns (host_name)
    for col in DIRECT_PII_COLUMNS:
        if col in df.columns:
            df = df.drop(columns=[col])

    # Step 2: Convert host_id to host_key
    if "host_id" in df.columns:
        df["host_key"] = df["host_id"].apply(pseudonymize_value)
        # Step 3: Drop the original host_id
        df = df.drop(columns=["host_id"])

    return df
