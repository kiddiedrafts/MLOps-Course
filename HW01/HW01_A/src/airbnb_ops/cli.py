from datetime import datetime

import typer
from rich import print as rprint

from airbnb_ops.config import PipelineConfig
from airbnb_ops.extract import read_csv_checked
from airbnb_ops.pii import handle_pii
from airbnb_ops.transform import build_neighbourhood_summary
from airbnb_ops.validate import validate_summary

app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Airbnb ops CLI."""
    
    if ctx.invoked_subcommand is None:
        raise typer.Exit()


@app.command("run")
def run():
    """Run the Airbnb ops pipeline."""

    config = PipelineConfig()

    rprint("[bold blue]Starting Airbnb ops pipeline...[/bold blue]")

    # Step 1: Read inputs
    rprint("Step 1: Reading input files...")
    listings = read_csv_checked(config.listings_path)
    segments = read_csv_checked(config.segments_path)
    rprint(f"  - Loaded {len(listings)} listings")
    rprint(f"  - Loaded {len(segments)} segment records")

    # Step 2: Handle PII
    rprint("Step 2: Handling PII...")
    listings_clean = handle_pii(listings)
    rprint("  - Removed direct PII columns")
    rprint("  - Pseudonymized host_id -> host_key")

    # Step 3: Transform
    rprint("Step 3: Building neighbourhood summary...")
    summary = build_neighbourhood_summary(listings_clean, segments)
    rprint(f"  - Created summary with {len(summary)} neighbourhoods")

    # Step 4: Validate
    rprint("Step 4: Validating output...")
    validate_summary(summary)
    rprint("  - All validation checks passed")

    # Save the CSV
    rprint("Step 5: Writing output CSV...")
    config.output_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(config.output_path, index=False)
    rprint(f"  - Saved to {config.output_path}")

    # Step 6: Write report
    rprint("Step 6: Writing run report...")
    config.report_path.parent.mkdir(parents=True, exist_ok=True)
    write_report(config, listings, summary)
    rprint(f"  - Saved to {config.report_path}")

    rprint("[bold green]Pipeline completed successfully![/bold green]")


def write_report(config: PipelineConfig, listings, summary):
    """Write a markdown report about the pipeline run."""

    report_content = f"""# HW01-A Run Report

## Run Details

- **Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Input listings**: {len(listings)} rows
- **Output neighbourhoods**: {len(summary)} rows

## Output Columns

{', '.join(summary.columns.tolist())}

## Summary Statistics

| Neighbourhood | Listings | Avg Price |
|---------------|----------|-----------|
"""
    for _, row in summary.iterrows():
        report_content += f"| {row['neighbourhood']} | {row['num_listings']} | {row['avg_price']:.2f} |\n"

    report_content += f"""
## Files

- Input: `{config.listings_path}`, `{config.segments_path}`
- Output: `{config.output_path}`
"""
    config.report_path.write_text(report_content)


if __name__ == "__main__":
    app()
