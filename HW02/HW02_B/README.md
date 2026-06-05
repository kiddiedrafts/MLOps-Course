# HW02-B: MLflow Experiment Tracking

Train and compare several model versions for the listing availability problem, with full experiment tracking in MLflow.

## Goal

Make every experiment reproducible:

- Which dataset version was used
- Which features were used
- Which model and parameters were trained
- Which metrics and artifacts were produced
- Which run is the final production candidate

## Quick Start

```bash
cd HW02/HW02_B
cp .env.example .env
pip install pandas numpy scikit-learn matplotlib mlflow pyarrow python-dotenv
jupyter notebook notebooks/02_mlflow_experiments_student.ipynb
```

Run the notebook from `HW02/HW02_B` or from `HW02/HW02_B/notebooks` — paths resolve via `PROJECT_ROOT`.

1. Fill in MLflow credentials in `.env`
2. Put HW02-A feature files under `data/features/` (or symlink from HW02-A)
3. Run all notebook sections through the final explanation

## MLflow Server

| Setting | Value |
|---------|-------|
| Tracking URI | `http://185.50.38.163:33014` |
| Credentials | Assigned MLflow username/password (not DB credentials) |
| Experiment | Your assigned experiment name, e.g. `qbc12_hw02_student_<username>` |

## Input Dataset

Expected files under `data/features/`:

```text
listing_availability_features_v1_audit_cleaned.parquet
listing_availability_features_v1_audit_cleaned.csv
listing_availability_features_v1_audit_cleaned_metadata.json
```

Target column: `high_demand_proxy` (binary high-demand proxy).

## MLflow Runs

| Run | Model | Purpose |
|-----|-------|---------|
| `v0_leaky_logistic_regression` | LogisticRegression + future column | Intentional leakage demo |
| `v1_dummy_baseline` | DummyClassifier | Floor baseline |
| `v2_clean_logistic_regression` | LogisticRegression | First clean model |
| `v3_balanced_logistic_regression` | LogisticRegression (`class_weight=balanced`) | Imbalance handling |
| `v4_threshold_0.30` … `0.60` | LogisticRegression | Threshold tuning |
| `v5_random_forest` | RandomForestClassifier | Nonlinear comparison |

Each run logs params, metrics, tags, artifacts (confusion matrix, reports), and a full sklearn `Pipeline`.

## Results Summary

| Run | F1 | ROC-AUC | Notes |
|-----|-----|---------|-------|
| v0 leaky | 0.999 | 0.999 | Invalid — uses `future_available_rate_30d` |
| v1 dummy | 0.865 | 0.500 | Always predicts majority class |
| v2 clean LR | 0.978 | 0.980 | Solid baseline |
| v3 balanced LR | 0.982 | 0.981 | Better precision/recall balance |
| v5 random forest | **0.986** | **0.987** | **Selected final candidate** |

**Selected run:** `v5_random_forest`  
Tagged with `selected_for_serving=true` and `production_candidate=true`.

## Project Structure

```
HW02_B/
├── notebooks/
│   └── 02_mlflow_experiments_student.ipynb   # Main notebook
├── data/
│   └── features/                             # HW02-A feature files (linked or copied)
├── outputs/
│   └── mlflow_artifacts/                     # Local run artifacts (gitignored)
├── .env                                      # MLflow credentials (gitignored)
├── .env.example
└── .gitignore
```

## Notebook Sections

1. Configure MLflow (`.env`)
2. Load HW02 dataset
3. Define target and forbidden columns
4. Build intentionally leaky feature set
5. Train/test split (stratified 80/20)
6. Preprocessing (`ColumnTransformer`)
7. Evaluation helpers
8. Artifact helpers
9. `run_mlflow_experiment()` helper
10–15. Log all experiment runs
16. Compare runs with `mlflow.search_runs`
17. Select final clean candidate
18. Final explanation

## Notes

- Do not commit `.env`, `.venv/`, or `outputs/`.
- Do not use future/label columns in the final clean model.
- MLflow client 3.x may need the notebook’s model-logging fallback for the shared tracking server.
- Reject the leaky run for production even if its metrics look best.
