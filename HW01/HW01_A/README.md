# HW01-A: Dockerized Airbnb Ops Package

A reproducible data pipeline that processes Airbnb listings data into neighbourhood-level summaries.

## Quick Start (Docker)

```bash
docker compose build
docker compose run --rm airbnb-ops
```

Outputs:
- `data/processed/airbnb_neighbourhood_summary.csv`
- `reports/hw01_a_run_report.md`

## Local Development

```bash
pip install -e .
airbnb-ops run
```

## DVC Pipeline

```bash
pip install -e .
dvc repro
dvc dag
```

## Project Structure

```
HW01_A/
├── src/airbnb_ops/     # Python package
│   ├── cli.py          # CLI entry point
│   ├── config.py       # Pipeline paths
│   ├── extract.py      # Data loading
│   ├── pii.py          # PII handling
│   ├── transform.py    # Data aggregation
│   └── validate.py     # Output validation
├── data/
│   ├── raw/            # Input CSVs
│   └── processed/      # Generated output
├── Dockerfile
├── docker-compose.yml
├── dvc.yaml
└── pyproject.toml
```

## Pipeline Steps

1. Read raw listings and segments
2. Handle PII (drop `host_name`, hash `host_id`)
3. Aggregate by neighbourhood
4. Validate output
5. Write CSV and report
