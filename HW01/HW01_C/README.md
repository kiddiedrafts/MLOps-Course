# HW01-C: Airflow Scheduled Pipeline

Automates HW01-B SQL work: refresh materialized view → validate → write report.

## DAG

- **ID:** `qbc12_hw01_samin_kakaei_airbnb_pipeline`
- **File:** `dags/qbc12_hw01_samin_kakaei_airbnb_pipeline.py`

## Deliverables

| File | Purpose |
|------|---------|
| `dags/qbc12_hw01_samin_kakaei_airbnb_pipeline.py` | Airflow DAG |
| `reports/hw01_c_airflow.md` | Workflow report |
| `screenshots/airflow_dag_graph.png` | DAG graph screenshot |
| `screenshots/airflow_success_run.png` | Successful run screenshot |

## Local syntax check

```bash
python3 -m py_compile dags/qbc12_hw01_samin_kakaei_airbnb_pipeline.py
```

See `reports/hw01_c_airflow.md` for Airflow URL and run steps.
