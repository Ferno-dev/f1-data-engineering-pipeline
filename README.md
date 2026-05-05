# F1 Data Engineering Tech Test
Practical data ingestion pipeline for OpenF1 with Dagster orchestration, SQL validation, and CI/CD quality gates.

## Overview

This project ingests two OpenF1 endpoints:
- `/drivers` for driver reference data
- `/laps` for lap telemetry and timing data

Engineering focus:
- reliable ingestion with retries and exponential backoff
- idempotent writes to raw storage
- timestamp-based incremental loading
- minimal Dagster orchestration with schedule
- SQL data validation with DuckDB
- CI/CD quality gates with GitHub Actions

## Repository Structure

```text
f1-data-pipeline/
├── README.md
├── requirements.txt
├── pyproject.toml
├── uv.lock
├── src/
│   ├── ingestion/
│   │   ├── api_client.py
│   │   ├── incremental_loader.py
│   │   ├── drivers.py
│   │   └── laps.py
│   └── storage/
│       └── parquet_writer.py
├── orchestration/
├── f1_data_pipeline/orchestration/
│   └── definitions.py
├── tests/
│   ├── unit/
│   │   ├── test_api_client.py
│   │   ├── test_dagster_assets_config.py
│   │   ├── test_incremental_loader.py
│   │   ├── test_ingestion.py
│   │   └── test_parquet_writer.py
│   └── sql/
│       ├── test_drivers.sql
│       ├── test_laps.sql
│       ├── sql_test_runner.py
│       └── test_sql_validation.py
├── .github/workflows/
│   ├── ci.yml
│   └── deploy.yml
├── data/raw/
└── config/
```

## Quick Start (Local)

1. Install dependencies:

```bash
uv sync
```

2. Run ingestion scripts:

```bash
uv run python -m src.ingestion.drivers
uv run python -m src.ingestion.laps
```

3. Run all checks locally:

```bash
uv run ruff check .
uv run pytest tests/ -v
uv run python tests/sql/sql_test_runner.py
```

4. Optional: run Dagster locally:

```bash
uv run dg dev
```

If port 3000 is busy, Dagster auto-selects another available port and prints it in terminal output.

## Part-by-Part Delivery

### Part 1: Data Ingestion and Storage

Implemented:
- fetches data from `/drivers` and `/laps`
- idempotent raw writes to Parquet under `data/raw/`
- timestamp-based incremental logic using watermarks

Notes:
- API client retries with exponential backoff for transient failures (429/5xx).

### Part 2: Orchestration with Dagster

Implemented:
- Dagster assets for drivers and laps
- ingestion job that runs assets sequentially
- retry handling in ingestion path
- materialization logging with timestamps
- daily schedule at 00:00 UTC

### Part 3: Data Validation with SQL

Implemented in `tests/sql/` using DuckDB over Parquet files.

Drivers tests:
1. primary key null check
2. uniqueness constraint check
3. schema/readability check
4. non-zero row count check

Laps tests:
1. composite key null check
2. positive lap duration check
3. valid timestamp check
4. non-zero row count check

Execution commands:

```bash
uv run python tests/sql/sql_test_runner.py
uv run pytest tests/sql/test_sql_validation.py -v
```

### Part 4: CI/CD Pipeline

Two workflows are implemented.

`ci.yml` (Pull Request to main):
- lint: `ruff`
- unit tests: `pytest tests/unit -v`
- SQL tests: `pytest tests/sql/test_sql_validation.py -v`

`deploy.yml` (Push to main):
- runs lint + unit + SQL tests again
- optional smoke pipeline run
- creates and uploads build artifact

Design choices:
- separate jobs for required status checks
- lint first for fast failure feedback
- re-validation on main for merge safety
- optional smoke test is non-blocking due external API variability

### Part 5: Documentation

This README provides:
- local run instructions
- troubleshooting guide
- pipeline monitoring approach
- failed run handling steps
- Generative AI disclosure

## Monitoring Pipeline Health

Use Dagster and CI signals together:
- Dagster asset materializations and run history
- run success/failure rate and execution duration
- schedule freshness (last successful run versus daily schedule)
- CI status checks on pull requests and main branch runs

## Handling Failed Runs

1. Check Dagster run logs and identify failing asset/step.
2. Validate OpenF1 API availability and HTTP status patterns.
3. Re-run failed ingestion job or asset (safe due idempotent writes).
4. Confirm watermark state for incremental loads.
5. Re-run quality gates locally:

```bash
uv run ruff check .
uv run pytest tests/ -v
```

6. If data quality failed, inspect generated Parquet files and rerun SQL tests.

## Troubleshooting Common Issues

- `uv run dg dev` fails:
  - run `uv sync` and retry
  - verify project root is current working directory
- OpenF1 temporary HTTP failures (429/5xx):
  - wait and retry (client backoff is already enabled)
- SQL tests fail with missing Parquet file:
  - run ingestion scripts first to populate `data/raw/`
- incremental loads return no rows unexpectedly:
  - inspect watermark file/state and endpoint filters
- CI fails but local passes:
  - run `uv sync --frozen` and rerun checks to mirror CI environment

## Final Validation Snapshot

Local final run status:
- lint passed
- unit tests passed
- SQL tests passed
- total pytest tests: 24 passed

## Packaging and Peer Handoff

Create a shareable package locally:

```bash
mkdir -p dist
tar -czf dist/f1-data-pipeline-peer-package.tar.gz \
  README.md pyproject.toml uv.lock src tests orchestration \
  f1_data_pipeline .github config
```

This archive is suitable for peer review and mirrors the CI-tested project content.

## Generative AI Disclosure

Generative AI was used to accelerate implementation and documentation.

Usage scope:
- drafting and refining workflow YAML
- validating command sequences and runbooks
- documentation structuring and clarity improvements

Verification policy:
- all generated changes were manually reviewed
- lint and tests were executed locally before submission
- final behavior was validated with project test suites
