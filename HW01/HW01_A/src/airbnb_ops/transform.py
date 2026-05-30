import pandas as pd


# Required columns in the input listings DataFrame
REQUIRED_LISTING_COLUMNS = [
    "listing_id",
    "neighbourhood",
    "price",
    "minimum_nights",
    "availability_365",
    "number_of_reviews",
]


# Take listing rows, group by neighbourhood, calculate stats
def build_neighbourhood_summary(
    listings: pd.DataFrame, segments: pd.DataFrame
) -> pd.DataFrame:
    """Build a neighbourhood-level summary from listings and segment data."""
    
    # Step 1: Validate required columns exist
    missing = set(REQUIRED_LISTING_COLUMNS) - set(listings.columns)
    if missing:
        raise ValueError(f"Missing required columns in listings: {missing}")

    # Step 2: Aggregate by neighbourhood using groupby
    summary = (
        listings.groupby("neighbourhood")
        .agg(
            num_listings=("listing_id", "count"),
            avg_price=("price", "mean"),
            median_price=("price", "median"),
            avg_minimum_nights=("minimum_nights", "mean"),
            availability_365_avg=("availability_365", "mean"),
            total_reviews=("number_of_reviews", "sum"),
        )
        .reset_index()
    )

    # Calculate reviews_per_listing
    summary["reviews_per_listing"] = summary["total_reviews"] / summary["num_listings"]

    # Step 3: Join with segments (left join to keep all neighbourhoods)
    summary = summary.merge(segments, on="neighbourhood", how="left")

    # Step 4: Fill missing segment values with 'unknown'
    summary["tourism_segment"] = summary["tourism_segment"].fillna("unknown")
    summary["priority_level"] = summary["priority_level"].fillna("unknown")

    return summary
