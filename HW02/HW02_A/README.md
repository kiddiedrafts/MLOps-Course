# HW02-A: Privacy-Aware Listing Availability ETL

Build a versioned ML feature dataset from the QBC12 Airbnb PostgreSQL database for the listing availability / high-demand prediction problem.

## Goal

- One row per `listing_id` at a fixed `cutoff_date`
- Features from data available on/before the cutoff
- Target from future calendar availability (30-day window)
- No raw PII in the final ML dataset

## Quick Start

```bash
cd HW02/HW02_A
# create .env with PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD
pip install pandas numpy sqlalchemy psycopg2-binary pyarrow python-dotenv
jupyter notebook notebooks/01_etl_pipeline_student.ipynb
```

Run the notebook from `HW02/HW02_A` (or ensure `PROJECT_ROOT` resolves correctly).

## Database

| Setting | Value |
|---------|-------|
| Host | `185.50.38.163` |
| Port | `32112` |
| Database | `qbc12_airbnb` |
| SSL | `sslmode=disable` |

Put credentials in `.env` (not committed). Use your assigned student DB user.

## Deliverables

Saved under `data/features/`:

| File | Purpose |
|------|---------|
| `listing_availability_features_<version>.csv` | Feature dataset (CSV) |
| `listing_availability_features_<version>.parquet` | Feature dataset (Parquet) |
| `listing_availability_features_<version>_metadata.json` | Version, cutoff, target definition |
| `listing_availability_features_<version>_validation_report.json` | QA checks |
| `pii_audit_<version>.csv` | PII column audit |

## Dataset Summary (`v1_student`)

| Field | Value |
|-------|-------|
| Rows | 10,480 |
| Columns | 33 |
| Model input columns | 26 |
| Cutoff date | `2026-08-11` |
| Past window | 90 days |
| Future window | 30 days |

**Target:** `high_demand_proxy`

```text
high_demand_proxy = 1  if  future_available_rate_30d <= 0.30
high_demand_proxy = 0  otherwise
```

## Project Structure

```
HW02_A/
├── notebooks/
│   └── 01_etl_pipeline_student.ipynb   # Main ETL notebook
├── data/
│   └── features/                       # Generated outputs
│       ├── listing_availability_features_v1_student.parquet
│       ├── listing_availability_features_v1_student.csv
│       ├── listing_availability_features_v1_student_metadata.json
│       ├── listing_availability_features_v1_student_validation_report.json
│       └── pii_audit_v1_student.csv
├── .env                                # DB credentials (gitignored)
└── .gitignore
```

## Pipeline Steps

1. Connect to PostgreSQL and verify access
2. Inspect source tables (`core.listing`, `core.calendar_day`, `core.review`, etc.)
3. Run PII audit and drop forbidden columns
4. Build past-window listing features (availability, reviews, listing attributes)
5. Build future-window label columns and `high_demand_proxy`
6. Validate uniqueness, missing target, leakage checks
7. Save versioned CSV, Parquet, metadata, validation report, PII audit

## Source Tables

- `core.listing`
- `core.host`
- `core.neighbourhood`
- `core.review`
- `core.calendar_day`

## Notes

- Do not commit `.env`, `.venv/`, or credentials.
- HW02-B uses this dataset for MLflow experiments — keep ETL outputs clean and versioned.
