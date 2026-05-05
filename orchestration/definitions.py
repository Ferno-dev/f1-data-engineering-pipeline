from datetime import datetime, timezone

from dagster import (
    AssetExecutionContext,
    AssetSelection,
    Definitions,
    MaterializeResult,
    ScheduleDefinition,
    asset,
    define_asset_job,
)

from src.ingestion.incremental_loader import ingest_incremental


@asset(name="drivers_asset")
def drivers_asset(context: AssetExecutionContext) -> MaterializeResult:
    result = ingest_incremental(
        endpoint="drivers",
        output_name="drivers",
        base_params={"session_key": "latest"},
    )
    materialized_at = datetime.now(timezone.utc).isoformat()

    context.log.info(
        "drivers_asset materialized at %s with %s records",
        materialized_at,
        result["records_fetched"],
    )

    return MaterializeResult(
        metadata={
            "path": result["path"],
            "records_fetched": result["records_fetched"],
            "previous_watermark": result["previous_watermark"] or "",
            "current_watermark": result["current_watermark"] or "",
            "materialized_at_utc": materialized_at,
        }
    )


@asset(name="laps_asset", deps=[drivers_asset])
def laps_asset(context: AssetExecutionContext) -> MaterializeResult:
    result = ingest_incremental(
        endpoint="laps",
        output_name="laps",
        timestamp_field="date_start",
        timestamp_param="date_start>",
        base_params={"session_key": "latest"},
    )
    materialized_at = datetime.now(timezone.utc).isoformat()

    context.log.info(
        "laps_asset materialized at %s with %s records",
        materialized_at,
        result["records_fetched"],
    )

    return MaterializeResult(
        metadata={
            "path": result["path"],
            "records_fetched": result["records_fetched"],
            "previous_watermark": result["previous_watermark"] or "",
            "current_watermark": result["current_watermark"] or "",
            "materialized_at_utc": materialized_at,
        }
    )


ingestion_job = define_asset_job(
    "ingestion_job", selection=AssetSelection.assets(drivers_asset, laps_asset)
)

daily_midnight_utc_schedule = ScheduleDefinition(
    job=ingestion_job,
    cron_schedule="0 0 * * *",
    execution_timezone="UTC",
)

defs = Definitions(
    assets=[drivers_asset, laps_asset],
    jobs=[ingestion_job],
    schedules=[daily_midnight_utc_schedule],
)