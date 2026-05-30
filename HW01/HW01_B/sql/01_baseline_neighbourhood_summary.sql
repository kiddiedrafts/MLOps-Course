
WITH calendar_30 AS (
    SELECT 
        listing_id,
        AVG(price) AS avg_calendar_price_30,
        AVG(CASE WHEN available THEN 1.0 ELSE 0.0 END) AS availability_30_rate
    FROM core.calendar_day
    WHERE date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY listing_id
),
review_counts AS (
    SELECT 
        listing_id,
        COUNT(*) AS total_reviews
    FROM core.review
    GROUP BY listing_id
)
SELECT 
    l.neighbourhood_id AS neighbourhood,
    COUNT(*) AS num_listings,
    AVG(l.listing_price) AS avg_price,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY l.listing_price) AS median_price,
    AVG(l.minimum_nights) AS avg_minimum_nights,
    COALESCE(SUM(r.total_reviews), 0) AS total_reviews,
    COALESCE(SUM(r.total_reviews), 0)::float / COUNT(*) AS reviews_per_listing,
    AVG(c.availability_30_rate) AS availability_30_rate
FROM core.listing l
LEFT JOIN calendar_30 c ON l.listing_id = c.listing_id
LEFT JOIN review_counts r ON l.listing_id = r.listing_id
GROUP BY l.neighbourhood_id
ORDER BY num_listings DESC
