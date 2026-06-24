# HW03 — Model Serving & Deployment

Take the HW02 model from MLflow, wrap it in a production-style FastAPI service, containerize it, and write Kubernetes manifests.

## Goal

- Verify the model is reproducible on the feature dataset
- Serve predictions through FastAPI with validation and batch support
- Compare single vs batch inference performance
- Build naive and optimized Docker images
- Write K8s Deployment and Service YAML

## Prerequisites

Complete **HW02-B** (MLflow experiment with a clean run tagged `selected_for_serving=true`) and **HW02-A** (feature parquet).

## Quick Start

```bash
cd HW03/HW03_model_serving
cp .env.example .env
# fill in MLflow credentials and MODEL_RUN_ID
pip install -e .
jupyter notebook notebooks/01_model_serving_student.ipynb
```

Run the API locally:

```bash
export MODEL_RUN_ID=your_hw02_run_id
uvicorn airbnb_serving.app:app --host 0.0.0.0 --port 8000
```

Swagger: `http://127.0.0.1:8000/docs`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service status and loaded `model_run_id` |
| POST | `/predict` | Single listing prediction |
| POST | `/predict/batch` | Batch predictions (JSON array, not `{records: [...]}`) |

Use `is_superhost` in request JSON (not `host_is_superhost`).

## Docker

```bash
docker build -f Dockerfile.naive -t qbc12-airbnb-serving:naive .
docker build -f Dockerfile -t qbc12-airbnb-serving:optimized .
docker compose up -d
```

Image sizes: naive **1.91GB**, optimized **923MB** (see `reports/docker_size_report.md`).

## Kubernetes

Manifests in `k8s/`:

- `deployment.yaml` — 2 replicas, Secret-backed env vars, readiness probe on `/health`
- `service.yaml` — ClusterIP, port 80 → 8000

No real cluster required for submission. Credentials go in a K8s Secret at deploy time, not in git.

## Project Structure

```text
HW03_model_serving/
├── notebooks/
│   └── 01_model_serving_student.ipynb   # Main homework notebook
├── src/airbnb_serving/                  # FastAPI app package
│   ├── app.py
│   ├── schema.py
│   └── predictor.py
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── reports/
│   └── docker_size_report.md
├── screenshots/                         # Swagger / Docker proof shots
├── Dockerfile
├── Dockerfile.naive
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
├── .env.example
└── .env                                 # gitignored
```

Feature data: `data/features/` points to the HW02-A parquet.

## Deliverables

| Item | Location |
|------|----------|
| FastAPI service | `src/airbnb_serving/` |
| Docker files | `Dockerfile`, `Dockerfile.naive`, `.dockerignore`, `docker-compose.yml` |
| Size report | `reports/docker_size_report.md` |
| K8s manifests | `k8s/deployment.yaml`, `k8s/service.yaml` |
| Screenshots | `screenshots/` (health, predict, batch, docs, image sizes) |
| Notebook | `notebooks/01_model_serving_student.ipynb` |

## Results Summary

| Item | Value |
|------|-------|
| Experiment | `qbc12_hw02_student_samin_kakaei` |
| Serving run | `a37a223cfd294ac2a27516b90d5a795c` (`v5_random_forest`, F1 ≈ 0.986) |
| Batch speedup | ~81× vs 100 single `/predict` calls (100-row benchmark) |

## Notes

- Work from this folder's root; the notebook sets `PROJECT` automatically.
- Do not commit `.env`, `.venv/`, passwords, or notebook checkpoints.
- Model loads from MLflow at startup — do not bake the pickle into the Docker image.
- Pin `scikit-learn==1.7.2` to match the trained model version.
