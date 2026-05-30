# Analyze Observations

## 1. Calendar Data Aggregation is the Main Bottleneck
The Finalize HashAggregate on `calendar_day` takes 440-450ms out of the total 593ms execution time (76%).
This operation reads 20,626 buffer pages from disk to aggregate availability data by listing_id.

## 2. HashAggregate Memory Usage
The HashAggregate operation uses 4,497kB of memory for the main aggregation.
Parallel workers (2 launched) each use approximately 2,449kB for partial aggregation.

## 3. Multiple Hash Join Operations  
The query performs two hash joins:
- Hash Right Join: connects calendar aggregation to listings (actual time: 458-472ms)
- Hash Left Join: connects review counts to the result (actual time: 565-583ms)
Total buffer pages read: 29,032 (shared hit=2, read=29,032 from disk)

## Conclusion
The query runs this expensive aggregation every time someone opens the dashboard.
A materialized view would pre-compute this once and make reads instant.
