import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.ingestion.incremental_loader import ingest_incremental


def test_ingest_incremental_first_run_sets_watermark(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    mock_client = MagicMock()
    mock_client.fetch_data.return_value = [
        {"driver_number": 1, "date": "2026-05-05T10:00:00Z"},
        {"driver_number": 16, "date": "2026-05-05T10:00:02Z"},
    ]

    with patch("src.ingestion.incremental_loader.write_to_parquet", return_value="data/raw/drivers.parquet"):
        result = ingest_incremental(
            endpoint="drivers",
            output_name="drivers",
            client=mock_client,
            state_path="data/state/watermarks.json",
        )

    mock_client.fetch_data.assert_called_once_with("drivers", params=None)
    assert result["previous_watermark"] is None
    assert result["current_watermark"] == "2026-05-05T10:00:02Z"
    assert result["watermark_updated"] is True

    state_data = json.loads(Path("data/state/watermarks.json").read_text(encoding="utf-8"))
    assert state_data["drivers"] == "2026-05-05T10:00:02Z"


def test_ingest_incremental_uses_existing_watermark(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    state_dir = Path("data/state")
    state_dir.mkdir(parents=True, exist_ok=True)
    Path("data/state/watermarks.json").write_text(
        json.dumps({"laps": "2026-05-05T09:00:00Z"}),
        encoding="utf-8",
    )

    mock_client = MagicMock()
    mock_client.fetch_data.return_value = [
        {"lap_number": 1, "date": "2026-05-05T09:00:01Z"},
        {"lap_number": 2, "date": "2026-05-05T09:00:05Z"},
    ]

    with patch("src.ingestion.incremental_loader.write_to_parquet", return_value="data/raw/laps.parquet"):
        result = ingest_incremental(
            endpoint="laps",
            output_name="laps",
            client=mock_client,
            state_path="data/state/watermarks.json",
        )

    mock_client.fetch_data.assert_called_once_with(
        "laps", params={"since": "2026-05-05T09:00:00Z"}
    )
    assert result["previous_watermark"] == "2026-05-05T09:00:00Z"
    assert result["current_watermark"] == "2026-05-05T09:00:05Z"


def test_ingest_incremental_does_not_regress_watermark(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("data/state").mkdir(parents=True, exist_ok=True)
    Path("data/state/watermarks.json").write_text(
        json.dumps({"drivers": "2026-05-05T10:00:00Z"}),
        encoding="utf-8",
    )

    mock_client = MagicMock()
    mock_client.fetch_data.return_value = [
        {"driver_number": 1, "date": "2026-05-05T09:59:00Z"}
    ]

    with patch("src.ingestion.incremental_loader.write_to_parquet", return_value="data/raw/drivers.parquet"):
        result = ingest_incremental(
            endpoint="drivers",
            output_name="drivers",
            client=mock_client,
            state_path="data/state/watermarks.json",
        )

    assert result["current_watermark"] == "2026-05-05T10:00:00Z"
    assert result["watermark_updated"] is False
