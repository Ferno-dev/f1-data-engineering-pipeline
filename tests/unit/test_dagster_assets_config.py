from unittest.mock import MagicMock, patch

from src.f1_data_pipeline.orchestration.definitions import drivers_asset, laps_asset


@patch("src.f1_data_pipeline.orchestration.definitions.ingest_incremental")
def test_drivers_asset_uses_scoped_base_params(mock_ingest):
    mock_ingest.return_value = {
        "path": "data/raw/drivers.parquet",
        "records_fetched": 1,
        "previous_watermark": None,
        "current_watermark": None,
    }

    mock_context = MagicMock()
    drivers_asset.op.compute_fn.decorated_fn(context=mock_context)

    mock_ingest.assert_called_once_with(
        endpoint="drivers",
        output_name="drivers",
        base_params={"session_key": "latest"},
    )


@patch("src.f1_data_pipeline.orchestration.definitions.ingest_incremental")
def test_laps_asset_uses_valid_incremental_params(mock_ingest):
    mock_ingest.return_value = {
        "path": "data/raw/laps.parquet",
        "records_fetched": 1,
        "previous_watermark": None,
        "current_watermark": None,
    }

    mock_context = MagicMock()
    laps_asset.op.compute_fn.decorated_fn(context=mock_context)

    mock_ingest.assert_called_once_with(
        endpoint="laps",
        output_name="laps",
        timestamp_field="date_start",
        timestamp_param="date_start>",
        base_params={"session_key": "latest"},
    )
