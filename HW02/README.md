# HW02 — Listing Availability ML (MLOps Course)

Three connected assignments: build a privacy-aware feature dataset, train and track models in MLflow, then serve the best model with FastAPI.

## Parts

| Folder | Topic | Start here |
|--------|-------|------------|
| [HW02_A](HW02_A/) | Privacy-aware ETL from PostgreSQL | `01_etl_pipeline_student.ipynb` |
| [HW02_B](HW02_B/) | MLflow experiment tracking and model selection | `02_mlflow_experiments_student.ipynb` |
| [HW02_C](HW02_C/) | FastAPI serving with Swagger | `student_hw02_fastapi_serving/` |

## Flow

```text
HW02-A  ETL → versioned feature dataset (no PII, no leakage)
   ↓
HW02-B  train/compare models → log to MLflow → pick production candidate
   ↓
HW02-C  load model from MLflow → expose /predict API → test in Swagger
```

## Problem

Predict **`high_demand_proxy`** for Airbnb listings: whether a listing will have low future availability (high demand) in the 30-day window after a fixed cutoff date.

| Setting | Value |
|---------|-------|
| Target | `high_demand_proxy` (1 = high demand, 0 = not) |
| Dataset version | `v1_audit_cleaned` |
| Model input features | 26 columns (listing, host, review, calendar history) |
| Forbidden inputs | `listing_id`, `cutoff_date`, future-window columns, target itself |

## Layout

```text
HW02/
├── HW02_A/   notebooks/, data/features/          # ETL outputs
├── HW02_B/   notebooks/, data/features/, outputs/ # MLflow experiments
└── HW02_C/   student_hw02_fastapi_serving/       # FastAPI app
                ├── app/
                ├── data/
                ├── screenshots/
                └── REPORT.md
```

Each subfolder has its own README with setup and deliverables.

## Shared Services

| Service | Used in | URI / access |
|---------|---------|--------------|
| PostgreSQL (`qbc12_airbnb`) | HW02-A | `185.50.38.163:32112` — student DB credentials |
| MLflow tracking server | HW02-B, HW02-C | `http://185.50.38.163:33014` — assigned MLflow user/password |

## Results Summary

| Part | Key outcome |
|------|-------------|
| HW02-A | `listing_availability_features_v1_audit_cleaned` — 10,480 rows, 26 model-input columns |
| HW02-B | Best clean run: `v5_random_forest` (F1 0.986, ROC-AUC 0.987), tagged for serving |
| HW02-C | FastAPI serves run `a37a223cfd294ac2a27516b90d5a795c` at `http://127.0.0.1:8000/docs` |

## Notes

- Work in each subfolder from that folder's root (notebooks use relative paths).
- Do not commit `.env`, `.venv/`, or credentials.
- HW02-B must finish before HW02-C — the API loads the model from your MLflow experiment.
- Reject leaky models for production even if their metrics look best.
