import pytest
from unittest.mock import MagicMock, patch
from requests.exceptions import HTTPError

from src.ingestion.api_client import OpenF1Client


@pytest.fixture
def client():
    return OpenF1Client()

# correct URL, params forwarded, JSON returned
def test_fetch_data_returns_json(client):
    mock_response = MagicMock()
    mock_response.json.return_value = [{"driver_number": 1, "name": "Max Verstappen"}]
    mock_response.raise_for_status.return_value = None

    with patch.object(client.session, "get", return_value=mock_response) as mock_get:
        result = client.fetch_data("drivers", params={"session_key": "latest"})

        mock_get.assert_called_once_with(
            "https://api.openf1.org/v1/drivers",
            params={"session_key": "latest"},
        )
        assert result == [{"driver_number": 1, "name": "Max Verstappen"}]

# Propagates HTTP errors
def test_fetch_data_raises_on_http_error(client):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = HTTPError("500 Server Error")

    with patch.object(client.session, "get", return_value=mock_response):
        with pytest.raises(HTTPError):
            client.fetch_data("drivers")

# Works when no params are provided
def test_fetch_data_no_params(client):
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status.return_value = None

    with patch.object(client.session, "get", return_value=mock_response) as mock_get:
        client.fetch_data("sessions")

        mock_get.assert_called_once_with(
            "https://api.openf1.org/v1/sessions",
            params=None,
        )

# Constructor accepts a custom base URL
def test_custom_base_url():
    custom_client = OpenF1Client(base_url="https://staging.openf1.org/v1")
    assert custom_client.base_url == "https://staging.openf1.org/v1"

# Retry adapter is attached to the session
def test_retry_adapter_mounted(client):
    adapter = client.session.get_adapter("https://api.openf1.org/v1/drivers")
    assert adapter is not None
