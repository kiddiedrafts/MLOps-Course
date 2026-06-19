from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict

FEATURE_COLS = [
    "room_type",
    "property_type",
    "neighbourhood_name",
    "accommodates",
    "bedrooms",
    "beds",
    "bathrooms",
    "listing_price",
    "minimum_nights",
    "maximum_nights",
    "instant_bookable",
    "is_superhost",
    "host_listing_count",
    "total_reviews_before_cutoff",
    "unique_reviewers_before_cutoff",
    "avg_comment_len_before_cutoff",
    "max_comment_len_before_cutoff",
    "days_since_last_review",
    "available_days_last_90d",
    "available_rate_last_90d",
    "avg_minimum_nights_calendar_last_90d",
    "avg_maximum_nights_calendar_last_90d",
    "available_days_last_30d",
    "available_rate_last_30d",
    "avg_minimum_nights_calendar_last_30d",
    "avg_maximum_nights_calendar_last_30d",
]


class ListingFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid")

    room_type: str
    property_type: str
    neighbourhood_name: str

    accommodates: int
    bedrooms: Optional[float] = None
    beds: Optional[float] = None
    bathrooms: Optional[float] = None
    listing_price: Optional[float] = None
    minimum_nights: int
    maximum_nights: int

    instant_bookable: bool
    is_superhost: Optional[bool] = None
    host_listing_count: int

    total_reviews_before_cutoff: float
    unique_reviewers_before_cutoff: float
    avg_comment_len_before_cutoff: Optional[float] = None
    max_comment_len_before_cutoff: Optional[float] = None
    days_since_last_review: float

    available_days_last_90d: int
    available_rate_last_90d: float
    avg_minimum_nights_calendar_last_90d: float
    avg_maximum_nights_calendar_last_90d: float

    available_days_last_30d: int
    available_rate_last_30d: float
    avg_minimum_nights_calendar_last_30d: float
    avg_maximum_nights_calendar_last_30d: float


class PredictionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    listing_id: int | None = None
    prediction: int
    probability_high_demand: float
    model_run_id: str
