# MLOps Course  

Submissions for the QBC12 MLOps bootcamp.

## Assignments

| HW | Topic | Overview |
|----|-------|----------|
| [HW01](HW01/) | Airbnb Ops | Docker pipeline, SQL optimization, Airflow scheduling |
| [HW02](HW02/) | Listing Availability ML | ETL, MLflow experiments, FastAPI serving |
| [HW03](HW03/) | Model Serving & Deployment | Versioned encoder bundle, Dockerized FastAPI, Kubernetes on k3s |

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

---

## HW03 — Model Serving & Deployment

Three connected assignments: freeze a versioned encoder bundle, containerize it as a FastAPI embedder service, then deploy to a shared k3s cluster with production-style Kubernetes scenarios.

| Folder | Topic | Start here |
|--------|-------|------------|
| [HW3_A](HW03/HW3_Student/HW3_A/) | Versioned encoder bundle, pytest, MLflow, MinIO upload | `encoder_bundle.ipynb` |
| [HW3_B](HW03/HW3_Student/HW3_B/) | FastAPI embedder, Docker image, compose smoke tests | `app/main.py`, `Makefile` |
| [HW3_C](HW03/HW3_Student/HW3_C/) | k3s deployment: probes, rolling updates, blue/green, HPA, PDB | `01_first_deployment/` → `07_prestop_and_eval/` |

```text
HW3-A  frozen bundle (predict.py + MANIFEST) → MLflow + MinIO
   ↓
HW3-B  FastAPI (/embed, /search, /health) → Docker image → registry push
   ↓
HW3-C  init container + probes → failure modes → rolling update → blue/green
       → HPA → PDB → preStop + verification → scale to zero
```

HW3_C work is organized into seven task folders under `HW03/HW3_Student/HW3_C/`. Each task has a `README.md`, Kubernetes manifests live in `k8s/`, and screenshots go in `EVIDENCE/`. See the [HW3_C README](HW03/HW3_Student/HW3_C/README.md) for submission details (13 screenshots + `k8s/*.yaml`).

