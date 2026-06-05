# HW02-C Submission Report

**Student:** Samin Kakaei (`student_samin_kakaei`)

## Selected HW02 MLflow run

| Field | Value |
|-------|-------|
| Run ID | `a37a223cfd294ac2a27516b90d5a795c` |
| Run name | `v5_random_forest` |
| Experiment | `qbc12_hw02_student_samin_kakaei` |
| Model URI | `runs:/a37a223cfd294ac2a27516b90d5a795c/model` |
| Dataset version | `v1_audit_cleaned` |
| Target | `high_demand_proxy` |
| Prediction threshold | `0.5` |

### Run metrics (from `/model-info`)

| Metric | Value |
|--------|-------|
| accuracy | 0.979 |
| precision | 0.982 |
| recall | 0.9906 |
| f1 | 0.9863 |
| roc_auc | 0.9872 |

### Run parameters

- `n_estimators`: 100
- `max_depth`: 10
- `min_samples_leaf`: 5
- `class_weight`: none
- `random_state`: 42
- `threshold`: 0.5

The API auto-selected this run because it is tagged `selected_for_serving=true` and `production_candidate=true` in HW02-B.

## Implementation summary

| Component | File | Status |
|-----------|------|--------|
| MLflow model loading | `app/model_loader.py` | Done |
| Feature validation | `app/predictor.py` | Done |
| Prediction logic | `app/predictor.py` | Done |
| API endpoints | `app/main.py` | Done |
| Request/response schemas | `app/schemas.py` | Done |
| Environment config | `app/config.py` + `.env` | Done |

### Endpoints

- `GET /` — service info
- `GET /health` — model load status
- `GET /model-info` — MLflow run metadata
- `POST /predict` — single listing prediction
- `POST /predict-batch` — batch prediction (up to 100 records)

Swagger UI: `http://127.0.0.1:8000/docs`

## Swagger test results

All tests were run with the JSON files in `data/`.

| Test file | Endpoint | Expected | Result |
|-----------|----------|----------|--------|
| `valid_predict_request.json` | `POST /predict` | 200 + prediction | Pass |
| `valid_batch_request.json` | `POST /predict-batch` | 200 + 2 predictions | Pass |
| `bad_request_missing_field.json` | `POST /predict` | 422 validation error | Pass |
| `bad_request_wrong_type.json` | `POST /predict` | 422 validation error | Pass |
| `bad_request_leakage_field.json` | `POST /predict` | 422 validation error | Pass |

### Example successful responses

**`POST /predict`** (private room, Centrum-West):

```json
{
  "prediction": 0,
  "prediction_label": "not_high_demand_proxy",
  "probability": 0.45916763206100947,
  "threshold": 0.5
}
```

**`POST /predict-batch`** (2 records):

```json
{
  "count": 2,
  "predictions": [
    {
      "prediction": 0,
      "prediction_label": "not_high_demand_proxy",
      "probability": 0.45916763206100947,
      "threshold": 0.5
    },
    {
      "prediction": 0,
      "prediction_label": "not_high_demand_proxy",
      "probability": 0.08216676932407103,
      "threshold": 0.5
    }
  ]
}
```

Probabilities below `0.5` correctly map to class `0` (`not_high_demand_proxy`).

### Leakage protection

The API rejects forbidden fields via Pydantic (`extra="forbid"`) and explicit validation in `predictor.py`:

- `listing_id`
- `cutoff_date`
- `dataset_version`
- `future_calendar_days_observed_30d`
- `future_available_days_30d`
- `future_available_rate_30d`
- `high_demand_proxy`

## Screenshots

Required screenshots are in `screenshots/`:

| File | Description |
|------|-------------|
| `01_docs_all_endpoints.png` | Swagger `/docs` showing all endpoints |
| `02_predict_schema.png` | `POST /predict` request schema |
| `03_predict_success.png` | Successful single prediction |
| `04_predict_validation_error.png` | Failed request (validation error) |
| `05_batch_predict_success.png` | Successful batch prediction |
| `06_model_info.png` | `GET /model-info` response |

Additional screenshots:

| File | Description |
|------|-------------|
| `07_root.png` | `GET /` response |
| `08_health.png` | `GET /health` response |
| `09_bad_request_leakage.png` | Leakage field rejected |
| `10_bad_request_missing_field.png` | Missing field rejected |

## How to run

```bash
cd HW02/HW02_C/student_hw02_fastapi_serving
cp .env.example .env   # fill in MLflow credentials
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Credentials are loaded automatically from `.env` via `python-dotenv` in `app/config.py`.
