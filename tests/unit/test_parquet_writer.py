from pathlib import Path

import pandas as pd

from src.storage.parquet_writer import write_to_parquet


def test_write_to_parquet_creates_file_and_returns_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    data = [{"driver_number": 1, "name": "Max Verstappen"}]
    returned_path = write_to_parquet(data, "drivers_latest")

    expected_path = Path("data/raw/drivers_latest.parquet")
    assert returned_path == str(expected_path)
    assert expected_path.exists()

    saved_df = pd.read_parquet(expected_path)
    assert saved_df.to_dict(orient="records") == data


def test_write_to_parquet_overwrites_existing_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    first_batch = [{"driver_number": 1, "name": "Max Verstappen"}]
    second_batch = [{"driver_number": 16, "name": "Charles Leclerc"}]

    write_to_parquet(first_batch, "drivers_latest")
    write_to_parquet(second_batch, "drivers_latest")

    saved_df = pd.read_parquet("data/raw/drivers_latest.parquet")
    assert saved_df.to_dict(orient="records") == second_batch


def test_write_to_parquet_handles_empty_data(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    returned_path = write_to_parquet([], "empty_batch")

    saved_df = pd.read_parquet(returned_path)
    assert saved_df.empty
