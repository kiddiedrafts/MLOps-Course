
-- Drop existing view if exists
DROP MATERIALIZED VIEW IF EXISTS "student_samin_kakaei".mv_airbnb_neighbourhood_summary;

-- Create materialized view
CREATE MATERIALIZED VIEW "student_samin_kakaei".mv_airbnb_neighbourhood_summary AS
WITH calendar_stats AS (
    SELECT 
        listing_id,
        AVG(CASE WHEN available THEN 1.0 ELSE 0.0 END) AS availability_365_rate,
        AVG(CASE WHEN date >= CURRENT_DATE - INTERVAL '30 days' 
            THEN (CASE WHEN available THEN 1.0 ELSE 0.0 END) 
            ELSE NULL END) AS availability_30_rate
    FROM core.calendar_day
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
    AVG(c.availability_30_rate) AS availability_30_rate,
    AVG(c.availability_365_rate) AS availability_365_rate
FROM core.listing l
LEFT JOIN calendar_stats c ON l.listing_id = c.listing_id
LEFT JOIN review_counts r ON l.listing_id = r.listing_id
GROUP BY l.neighbourhood_id;

-- Create index 1: on neighbourhood (for filtering)
CREATE INDEX idx_mv_neighbourhood 
ON "student_samin_kakaei".mv_airbnb_neighbourhood_summary (neighbourhood);

-- Create index 2: on num_listings (for sorting)
CREATE INDEX idx_mv_num_listings 
ON "student_samin_kakaei".mv_airbnb_neighbourhood_summary (num_listings DESC);
