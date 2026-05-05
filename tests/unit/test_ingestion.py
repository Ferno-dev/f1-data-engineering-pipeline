"""Unit tests for ingestion modules (drivers and laps)."""

from src.ingestion.drivers import ingest_drivers
from src.ingestion.laps import ingest_laps


def test_ingest_drivers_returns_result_dict():
    """Verify ingest_drivers runs and returns expected result structure."""
    result = ingest_drivers()

    assert isinstance(result, dict)
    assert "path" in result
    assert "records_fetched" in result
    assert result["records_fetched"] >= 0


def test_ingest_laps_returns_result_dict():
    """Verify ingest_laps runs and returns expected result structure."""
    result = ingest_laps()

    assert isinstance(result, dict)
    assert "path" in result
    assert "records_fetched" in result
    assert result["records_fetched"] >= 0
