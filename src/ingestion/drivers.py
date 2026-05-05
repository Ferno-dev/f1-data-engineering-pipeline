try:
    from ingestion.incremental_loader import ingest_incremental
except ModuleNotFoundError:
    from src.ingestion.incremental_loader import ingest_incremental


def ingest_drivers():
    """Ingest drivers endpoint and store as Parquet."""
    result = ingest_incremental(
        endpoint="drivers",
        output_name="drivers",
        timestamp_field=None,
        base_params={"session_key": "latest"},
    )
    print(f"Drivers ingestion: {result['records_fetched']} records, path={result['path']}")
    return result


if __name__ == "__main__":
    ingest_drivers()
