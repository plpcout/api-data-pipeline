import pytest

from ingest_data import (
    _convert_timestamp_to_iso,
    _generate_date_ranges,
    _process_earthquake_record,
    build_destination_bq_dataset,
    build_destination_bucket_path,
)


class TestConvertTimestampToIso:
    def test_known_timestamp(self):
        assert _convert_timestamp_to_iso(1609459200000) == "2021-01-01T00:00:00Z"

    def test_zero_timestamp(self):
        assert _convert_timestamp_to_iso(0) == "1970-01-01T00:00:00Z"

    def test_large_timestamp(self):
        assert "2025" in _convert_timestamp_to_iso(1750076400000)

    def test_microseconds_stripped(self):
        result = _convert_timestamp_to_iso(1609459200123)
        assert result.endswith("Z")
        assert ".123" not in result


class TestProcessEarthquakeRecord:
    def test_complete_record(self, sample_earthquake_record):
        result = _process_earthquake_record(sample_earthquake_record)
        assert result is not None
        props = result["properties"]

        assert "2021-01-01" in props["time"]
        assert "2021-01-02" in props["updated"]

        assert props["g_longitude"] == -155.233
        assert props["g_latitude"] == 19.446
        assert props["g_depth"] == 5.0
        assert props["g_type"] == "Point"

        assert "geometry" not in result

        assert props["country"] == "United States"
        assert props["country_code"] == "US"
        assert props["city"] == "Volcano"
        assert props["state"] == "Hawaii"
        assert props["population"] == 2575

    def test_record_without_geometry_returns_none(self, sample_record_no_geometry):
        assert _process_earthquake_record(sample_record_no_geometry) is None

    def test_original_properties_preserved(self, sample_earthquake_record):
        result = _process_earthquake_record(sample_earthquake_record)
        props = result["properties"]
        assert props["mag"] == 4.5
        assert props["type"] == "earthquake"
        assert props["tsunami"] == 0


class TestGenerateDateRanges:
    def test_january(self):
        assert _generate_date_ranges("2024", "01") == ("2024-01-01", "2024-01-31")

    def test_february_leap_year(self):
        assert _generate_date_ranges("2024", "02") == ("2024-02-01", "2024-02-29")

    def test_february_non_leap_year(self):
        assert _generate_date_ranges("2023", "02") == ("2023-02-01", "2023-02-28")

    def test_april_30_days(self):
        _, end = _generate_date_ranges("2024", "04")
        assert end == "2024-04-30"

    def test_december(self):
        _, end = _generate_date_ranges("2024", "12")
        assert end == "2024-12-31"


class TestBuildDestinationBucketPath:
    def test_with_env_var_set(self, monkeypatch):
        monkeypatch.setenv("DESTINATION__FILESYSTEM__BUCKET_URL", "gs://my-bucket")
        result = build_destination_bucket_path()
        assert "gs://my-bucket" in result
        assert "earthquakes_data" in result
        assert "raw" in result

    def test_without_env_var_raises(self, monkeypatch):
        monkeypatch.delenv("DESTINATION__FILESYSTEM__BUCKET_URL", raising=False)
        with pytest.raises(ValueError):
            build_destination_bucket_path()


class TestBuildDestinationBqDataset:
    def test_with_env_var_set(self, monkeypatch):
        monkeypatch.setenv("DESTINATION__BIGQUERY__DATASET_NAME", "dev_raw")
        assert build_destination_bq_dataset() == "dev_raw"

    def test_without_env_var_raises(self, monkeypatch):
        monkeypatch.delenv("DESTINATION__BIGQUERY__DATASET_NAME", raising=False)
        with pytest.raises(ValueError):
            build_destination_bq_dataset()
