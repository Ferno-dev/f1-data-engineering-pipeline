try:
    from ingestion.incremental_loader import ingest_incremental
except ModuleNotFoundError:
    from src.ingestion.incremental_loader import ingest_incremental

import pandas as pd


def ingest_laps():
    """Ingest laps endpoint and store as Parquet."""
    result = ingest_incremental(
        endpoint="laps",
        output_name="laps",
        timestamp_field="date_start",
        timestamp_param="date_start>",
        base_params={"session_key": "latest"},
    )
    
    # Filter out invalid lap durations (< 0)
    df = pd.read_parquet(result["path"])
    original_count = len(df)
    df = df[df["lap_duration"] >= 0]
    filtered_count = len(df)
    df.to_parquet(result["path"])
    
    print(f"Laps ingestion: {result['records_fetched']} records fetched, {original_count} original, {filtered_count} after filtering invalid durations, path={result['path']}")
    return result


if __name__ == "__main__":
    ingest_laps()
