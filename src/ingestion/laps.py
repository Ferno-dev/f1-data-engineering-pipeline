try:
    from ingestion.incremental_loader import ingest_incremental
except ModuleNotFoundError:
    from src.ingestion.incremental_loader import ingest_incremental


def ingest_laps():
    """Ingest laps endpoint and store as Parquet."""
    result = ingest_incremental(
        endpoint="laps",
        output_name="laps",
        timestamp_field="date_start",
        timestamp_param="date_start>",
        base_params={"session_key": "latest"},
    )
    print(f"Laps ingestion: {result['records_fetched']} records, path={result['path']}")
    return result


if __name__ == "__main__":
    ingest_laps()
