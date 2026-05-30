"""
HW01-C: Airbnb neighbourhood summary pipeline.

Workflow:
  read_config -> refresh_summary -> validate_summary -> branch -> success/failure report
"""

from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote_plus

from airflow.decorators import dag, task
from airflow.models import Variable
from sqlalchemy import create_engine, text

# Fixed per course naming (Excel username, not GitHub id)
DAG_ID = "qbc12_hw01_samin_kakaei_airbnb_pipeline"
STUDENT_SCHEMA = "student_samin_kakaei"
MV_NAME = "mv_airbnb_neighbourhood_summary"


def make_engine():
    """Build a SQLAlchemy engine using credentials from Airflow Variables."""
    host = Variable.get("qbc12_db_host")
    port = Variable.get("qbc12_db_port")
    db_name = Variable.get("qbc12_db_name")
    user = Variable.get("qbc12_db_user")
    password = Variable.get("qbc12_db_password")

    safe_password = quote_plus(password)
    url = f"postgresql+psycopg2://{user}:{safe_password}@{host}:{port}/{db_name}"
    return create_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 30})


def _build_refresh_sql(schema: str, view_name: str) -> list[str]:
    """SQL statements to recreate the materialized view and indexes."""
    qualified = f'"{schema}".{view_name}'
    return [
        f"DROP MATERIALIZED VIEW IF EXISTS {qualified}",
        f"""
        CREATE MATERIALIZED VIEW {qualified} AS
        WITH calendar_stats AS (
            SELECT
                listing_id,
                AVG(CASE WHEN available THEN 1.0 ELSE 0.0 END) AS availability_365_rate,
                AVG(
                    CASE
                        WHEN date >= CURRENT_DATE - INTERVAL '30 days'
                        THEN (CASE WHEN available THEN 1.0 ELSE 0.0 END)
                        ELSE NULL
                    END
                ) AS availability_30_rate
            FROM core.calendar_day
            GROUP BY listing_id
        ),
        review_counts AS (
            SELECT listing_id, COUNT(*) AS total_reviews
            FROM core.review
            GROUP BY listing_id
        )
        SELECT
            l.neighbourhood_id AS neighbourhood,
            COUNT(*) AS num_listings,
            AVG(l.listing_price) AS avg_price,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY l.listing_price) AS median_price,
            AVG(l.minimum_nights) AS avg_minimum_nights,
            COALESCE(SUM(r.total_reviews), 0) AS total_reviews,
            COALESCE(SUM(r.total_reviews), 0)::float / COUNT(*) AS reviews_per_listing,
            AVG(c.availability_30_rate) AS availability_30_rate,
            AVG(c.availability_365_rate) AS availability_365_rate
        FROM core.listing l
        LEFT JOIN calendar_stats c ON l.listing_id = c.listing_id
        LEFT JOIN review_counts r ON l.listing_id = r.listing_id
        GROUP BY l.neighbourhood_id
        """,
        f"CREATE INDEX IF NOT EXISTS idx_mv_neighbourhood ON {qualified} (neighbourhood)",
        f"CREATE INDEX IF NOT EXISTS idx_mv_num_listings ON {qualified} (num_listings DESC)",
    ]


@dag(
    dag_id=DAG_ID,
    description="Refresh Airbnb neighbourhood MV, validate, and write run report",
    schedule=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["qbc12", "hw01", "airbnb"],
    default_args={
        "owner": "samin_kakaei",
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
    },
)
def airbnb_pipeline():
    @task
    def read_config() -> dict:
        """Load pipeline settings. DB secrets stay in Airflow Variables."""
        return {
            "student_schema": Variable.get(
                "qbc12_student_schema", default_var=STUDENT_SCHEMA
            ),
            "materialized_view": MV_NAME,
            "report_dir": "reports",
        }

    @task
    def refresh_summary(config: dict) -> dict:
        """Recreate materialized view and indexes in Postgres (SQL only, no DataFrame)."""
        schema = config["student_schema"]
        view_name = config["materialized_view"]
        qualified = f'"{schema}".{view_name}'

        engine = make_engine()
        with engine.begin() as conn:
            conn.execute(text("SET statement_timeout = '120s'"))
            for stmt in _build_refresh_sql(schema, view_name):
                conn.execute(text(stmt))
            row_count = conn.execute(
                text(f"SELECT COUNT(*) FROM {qualified}")
            ).scalar()

        return {
            "student_schema": schema,
            "materialized_view": view_name,
            "qualified_name": qualified,
            "row_count": int(row_count),
            "status": "refreshed",
        }

    @task
    def validate_summary(config: dict) -> dict:
        """Run validation checks on the materialized view (SQL only)."""
        schema = config["student_schema"]
        view_name = config["materialized_view"]
        qualified = f'"{schema}".{view_name}'

        check_sql = text(
            f"""
            SELECT
                COUNT(*) AS row_count,
                COUNT(*) FILTER (WHERE neighbourhood IS NULL) AS null_neighbourhoods,
                COUNT(*) FILTER (
                    WHERE avg_price IS NULL OR avg_price < 0
                ) AS bad_prices,
                COUNT(*) FILTER (
                    WHERE availability_30_rate IS NULL
                       OR availability_30_rate < 0
                       OR availability_30_rate > 1
                       OR availability_365_rate IS NULL
                       OR availability_365_rate < 0
                       OR availability_365_rate > 1
                ) AS bad_availability
            FROM {qualified}
            """
        )

        engine = make_engine()
        with engine.connect() as conn:
            row = conn.execute(check_sql).mappings().one()

        row_count = int(row["row_count"])
        null_neighbourhoods = int(row["null_neighbourhoods"])
        bad_prices = int(row["bad_prices"])
        bad_availability = int(row["bad_availability"])

        checks = {
            "row_count_gt_0": row_count > 0,
            "null_neighbourhoods_eq_0": null_neighbourhoods == 0,
            "bad_prices_eq_0": bad_prices == 0,
            "bad_availability_eq_0": bad_availability == 0,
        }

        return {
            "qualified_name": qualified,
            "row_count": row_count,
            "null_neighbourhoods": null_neighbourhoods,
            "bad_prices": bad_prices,
            "bad_availability": bad_availability,
            "checks": checks,
            "passed": all(checks.values()),
        }

    @task.branch
    def choose_report_path(validation: dict) -> str:
        """Pick success or failure report task based on validation."""
        if validation["passed"]:
            return "write_success_report"
        return "write_failure_report"

    @task
    def write_success_report(
        config: dict, refreshed: dict, validation: dict
    ) -> dict:
        """Write a success report (different format from failure)."""
        report_dir = Path(config["report_dir"])
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "hw01_c_run_success.md"
        run_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        content = f"""# HW01-C Pipeline Run — SUCCESS

**DAG:** `{DAG_ID}`  
**Run time:** {run_time}  
**Status:** All validation checks passed.

## Refreshed object
- **Qualified name:** `{refreshed["qualified_name"]}`
- **Row count:** {refreshed["row_count"]}

## Validation summary
| Check | Result |
|-------|--------|
| row_count > 0 | {validation["row_count"]} rows |
| null_neighbourhoods == 0 | {validation["null_neighbourhoods"]} nulls |
| bad_prices == 0 | {validation["bad_prices"]} bad rows |
| bad_availability == 0 | {validation["bad_availability"]} bad rows |

**Overall:** PASSED
"""
        report_path.write_text(content)
        return {"report_path": str(report_path), "status": "success"}

    @task
    def write_failure_report(
        config: dict, refreshed: dict, validation: dict
    ) -> dict:
        """Write a failure report, then fail the DAG run."""
        report_dir = Path(config["report_dir"])
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "hw01_c_run_failure.md"
        run_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        failed = [
            name
            for name, ok in validation["checks"].items()
            if not ok
        ]

        content = f"""# HW01-C Pipeline Run — FAILURE

**DAG:** `{DAG_ID}`  
**Run time:** {run_time}  
**Status:** Validation failed — pipeline marked as failed.

## Refreshed object (may be incomplete)
- **Qualified name:** `{refreshed["qualified_name"]}`
- **Row count:** {refreshed["row_count"]}

## Failed checks
{chr(10).join(f"- {name}" for name in failed) or "- (unknown)"}

## Validation details
| Metric | Value |
|--------|-------|
| row_count | {validation["row_count"]} |
| null_neighbourhoods | {validation["null_neighbourhoods"]} |
| bad_prices | {validation["bad_prices"]} |
| bad_availability | {validation["bad_availability"]} |

**Overall:** FAILED — see checks above.
"""
        report_path.write_text(content)
        raise ValueError(
            f"Validation failed for {validation['qualified_name']}: {failed}"
        )

    config = read_config()
    refreshed = refresh_summary(config)
    validated = validate_summary(config)
    branch = choose_report_path(validated)
    success = write_success_report(config, refreshed, validated)
    failure = write_failure_report(config, refreshed, validated)

    refreshed >> validated >> branch
    branch >> [success, failure]


airbnb_pipeline()
