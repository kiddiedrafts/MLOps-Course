# MLOps Course  

Submissions for the QBC12 MLOps bootcamp.

## Assignments

| HW | Topic | Overview |
|----|-------|----------|
| [HW01](HW01/) | Airbnb Ops | Docker pipeline, SQL optimization, Airflow scheduling |
| [HW02](HW02/) | Listing Availability ML | ETL, MLflow experiments, FastAPI serving |

Each homework folder has its own README with setup, flow, and deliverables.

---

## HW01 — Airbnb Ops

Three connected assignments: package a data pipeline, optimize SQL for analytics, then schedule it in Airflow.

| Folder | Topic | Start here |
|--------|-------|------------|
| [HW01_A](HW01/HW01_A/) | Dockerized Python package, CLI, DVC | `01_dockerized_package_student.ipynb` |
| [HW01_B](HW01/HW01_B/) | SQL performance, materialized views, Metabase | `02_sql_performance_metabase_student.ipynb` |
| [HW01_C](HW01/HW01_C/) | Airflow DAG on shared services | `03_airflow_pipeline_student.ipynb` |

```text
HW01-A  local pipeline (Docker + DVC)
   ↓
HW01-B  Postgres queries + materialized view
   ↓
HW01-C  Airflow refreshes the view on a schedule
```

---

## HW02 — Listing Availability ML

Three connected assignments: build a privacy-aware feature dataset, train and track models in MLflow, then serve the best model with FastAPI.

| Folder | Topic | Start here |
|--------|-------|------------|
| [HW02_A](HW02/HW02_A/) | Privacy-aware ETL from PostgreSQL | `01_etl_pipeline_student.ipynb` |
| [HW02_B](HW02/HW02_B/) | MLflow experiment tracking and model selection | `02_mlflow_experiments_student.ipynb` |
| [HW02_C](HW02/HW02_C/) | FastAPI serving with Swagger | `student_hw02_fastapi_serving/` |

```text
HW02-A  ETL → versioned feature dataset (no PII, no leakage)
   ↓
HW02-B  train/compare models → log to MLflow → pick production candidate
   ↓
HW02-C  load model from MLflow → expose /predict API → test in Swagger
```

## Notes

- Work in each subfolder from that folder's root (notebooks use relative paths).
- Do not commit `.env`, `.venv/`, or credentials.
- HW01 B/C use shared course Postgres, Metabase, and Airflow.
- HW02 B/C use shared course Postgres and MLflow tracking server.
