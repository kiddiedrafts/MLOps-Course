# HW01-B: SQL Performance & Materialized Views

Optimizing Airbnb neighbourhood analytics queries using PostgreSQL materialized views.

## Summary

| Metric | Baseline | Optimized | Speedup |
|--------|----------|-----------|---------|
| Server execution | 593ms | 0.2ms | ~2,900x |
| Wall-clock (remote) | 7.25s | 1.89s | ~4x |

## Project Structure

```
HW01_B/
├── sql/
│   ├── 01_baseline_neighbourhood_summary.sql  # Original slow query
│   └── 02_create_materialized_view.sql        # Optimized view + indexes
├── reports/
│   ├── baseline_explain_analyze.txt           # Query execution plan
│   ├── explain_notes.md                       # Bottleneck analysis
│   └── hw01_b_sql_performance.md              # Performance report
└── 02_sql_performance_metabase_student.ipynb  # Main notebook
```

## What Was Done

### 1. Baseline Query
- Joins `core.listing` (10K rows), `core.calendar_day` (3.8M rows), `core.review` (500K rows)
- Aggregates by neighbourhood
- Takes ~593ms server-side per execution

### 2. Bottleneck Analysis (EXPLAIN ANALYZE)
- Main bottleneck: HashAggregate on `calendar_day` (76% of execution time)
- Buffer reads: 29,032 pages from disk
- Parallel workers: 2 launched for aggregation

### 3. Optimization: Materialized View
- Pre-computes the neighbourhood summary once
- Stores 22 rows in `student_samin_kakaei.mv_airbnb_neighbourhood_summary`
- Adds 2 indexes for fast filtering and sorting
- Server execution drops to 0.2ms

## Key Files

| File | Description |
|------|-------------|
| `sql/01_baseline_neighbourhood_summary.sql` | Original query with CTEs |
| `sql/02_create_materialized_view.sql` | CREATE MATERIALIZED VIEW + indexes |
| `reports/baseline_explain_analyze.txt` | Full EXPLAIN ANALYZE output |
| `reports/explain_notes.md` | 3 specific observations from query plan |
| `reports/hw01_b_sql_performance.md` | Final performance comparison report |

## Database Schema

- Schema: `student_samin_kakaei`
- View: `mv_airbnb_neighbourhood_summary`
- Indexes: `idx_mv_neighbourhood`, `idx_mv_num_listings`

## Output Columns

```
neighbourhood, num_listings, avg_price, median_price,
avg_minimum_nights, total_reviews, reviews_per_listing,
availability_30_rate, availability_365_rate
```
