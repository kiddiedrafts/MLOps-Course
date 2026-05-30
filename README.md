# HW01 — Airbnb Ops (MLOps Course)

Three connected assignments: package a data pipeline, optimize SQL for analytics, then schedule it in Airflow.

## Parts

| Folder | Topic | Start here |
|--------|-------|------------|
| [HW01_A](HW01_A/) | Dockerized Python package, CLI, DVC | `01_dockerized_package_student.ipynb` |
| [HW01_B](HW01_B/) | SQL performance, materialized views, Metabase | `02_sql_performance_metabase_student.ipynb` |
| [HW01_C](HW01_C/) | Airflow DAG on shared services | `03_airflow_pipeline_student.ipynb` |

## Flow

```text
HW01-A  local pipeline (Docker + DVC)
   ↓
HW01-B  Postgres queries + materialized view
   ↓
HW01-C  Airflow refreshes the view on a schedule
```

## Layout

```text
HW01/
├── HW01_A/   src/, data/, Dockerfile, dvc.yaml
├── HW01_B/   sql/, reports/, notebook
└── HW01_C/   dags/, reports/, screenshots/, notebook
```

Each subfolder has its own README with setup and deliverables.

## Notes

- Work in each subfolder from that folder’s root (notebooks use relative paths).
- Do not commit `.env`, `.venv/`, or credentials.
- B and C use shared course Postgres, Metabase, and Airflow (see the HW page).
