# HW01-B SQL Performance Report
## Schema
- Student Schema: `student_samin_kakaei`
- Materialized View: `mv_airbnb_neighbourhood_summary`

## Performance Comparison
### Wall-Clock Time (includes network latency)
| Query | Best Time (s) | Avg Time (s) | Speedup |
|-------|---------------|--------------|---------|
| Baseline (direct query) | 7.250 | 9.270 | 1.00x |
| Materialized View | 1.890 | 6.695 | 3.84x |

### Server Execution Time (from EXPLAIN ANALYZE)
| Query | Server Time | Speedup |
|-------|-------------|---------|
| Baseline (direct query) | ~593ms | 1x |
| Materialized View | **0.205ms** | **~2,900x** |

> **Note**: The large difference between wall-clock and server time is due to network latency 
> to the remote shared database server. In a production environment with local database access,
> the materialized view would be near-instant.

## What Changed
1. **Baseline Query**: Joins `core.listing`, `core.calendar_day` (3.8M rows), and `core.review` (500K rows) every time
2. **Optimized Query**: Reads pre-computed results from materialized view (22 rows)
3. **Indexes Added**: 
   - `idx_mv_neighbourhood` for filtering
   - `idx_mv_num_listings` for sorting

## Bottleneck Analysis (from EXPLAIN ANALYZE)
### Baseline Query
- Main bottleneck: HashAggregate on `calendar_day` table (3.8M rows)
- Calendar aggregation took ~450ms of ~593ms server execution time (76%)
- Buffer reads: 29,032 pages total
### Materialized View Read
- Simple sequential scan on 22 pre-computed rows
- Buffer reads: 1 page (shared hit)
- Server execution: 0.205ms

## Conclusion
The materialized view provides:
- **~2,900x server-side speedup** (593ms → 0.2ms)
- **~4x wall-clock speedup** (7.25s → 1.89s, limited by network latency)
The optimization successfully eliminates the expensive calendar_day aggregation by pre-computing results.
