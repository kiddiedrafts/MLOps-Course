import pandas as pd


# Required columns in the output summary
REQUIRED_OUTPUT_COLUMNS = {
    "neighbourhood",
    "num_listings",
    "avg_price",
    "median_price",
    "avg_minimum_nights",
    "availability_365_avg",
    "total_reviews",
    "reviews_per_listing",
    "tourism_segment",
    "priority_level",
}

# PII columns that must NOT exist in the output
PII_COLUMNS = {
    "host_name",
    "host_id",
    "reviewer_name",
    "reviewer_id",
    "listing_url",
    "host_url",
}


# Check that the output data is valid
def validate_summary(summary: pd.DataFrame) -> None:
    """Validate the neighbourhood summary DataFrame."""
    
    # Check 1: Output is not empty
    if summary.empty:
        raise ValueError("Output is empty")

    # Check 2: Required output columns exist
    missing_cols = REQUIRED_OUTPUT_COLUMNS - set(summary.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
 
    # Check 3: No PII columns exist
    pii_found = PII_COLUMNS & set(summary.columns)
    if pii_found:
        raise ValueError(f"PII columns found in output: {pii_found}")

    # Check 4: neighbourhood is not null
    if summary["neighbourhood"].isnull().any():
        raise ValueError("neighbourhood contains null values")

    # Check 5: num_listings > 0
    if (summary["num_listings"] <= 0).any():
        raise ValueError("num_listings must be greater than 0")

    # Check 6: avg_price >= 0
    if (summary["avg_price"] < 0).any():
        raise ValueError("avg_price cannot be negative")

    # Check 7: availability_365_avg between 0 and 365
    if (summary["availability_365_avg"] < 0).any():
        raise ValueError("availability_365_avg cannot be negative")
    if (summary["availability_365_avg"] > 365).any():
        raise ValueError("availability_365_avg cannot exceed 365")
