import json
from pathlib import Path

try:
    from ingestion.api_client import OpenF1Client
    from storage.parquet_writer import write_to_parquet
except ModuleNotFoundError:
    from src.ingestion.api_client import OpenF1Client
    from src.storage.parquet_writer import write_to_parquet


def _load_watermarks(state_path):
    path = Path(state_path)
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as state_file:
        return json.load(state_file)


def _save_watermarks(watermarks, state_path):
    path = Path(state_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as state_file:
        json.dump(watermarks, state_file, indent=2, sort_keys=True)


def _max_timestamp(records, timestamp_field):
    timestamps = [record.get(timestamp_field) for record in records if record.get(timestamp_field)]
    if not timestamps:
        return None
    return max(timestamps)


def ingest_incremental(
    endpoint,
    output_name,
    timestamp_field="date",
    timestamp_param="since",
    base_params=None,
    client=None,
    state_path="data/state/watermarks.json",
):
    """Fetch endpoint data incrementally and persist the watermark.

    The watermark is the max value found in timestamp_field for the endpoint.
    """
    api_client = client or OpenF1Client()
    params = dict(base_params or {})

    watermarks = _load_watermarks(state_path)
    previous_watermark = watermarks.get(endpoint)
    if previous_watermark is not None:
        params[timestamp_param] = previous_watermark

    data = api_client.fetch_data(endpoint, params=params or None)
    output_path = write_to_parquet(data, output_name)

    current_max_timestamp = _max_timestamp(data, timestamp_field)
    watermark_updated = False
    if current_max_timestamp and (
        previous_watermark is None or current_max_timestamp > previous_watermark
    ):
        watermarks[endpoint] = current_max_timestamp
        _save_watermarks(watermarks, state_path)
        watermark_updated = True

    return {
        "path": output_path,
        "records_fetched": len(data),
        "previous_watermark": previous_watermark,
        "current_watermark": watermarks.get(endpoint),
        "watermark_updated": watermark_updated,
        "params": params,
    }
