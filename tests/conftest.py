import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Kestra runtime is only available inside the Kestra container; stub it out so
# ingest_data can be imported in a plain pytest environment.
sys.modules["kestra"] = MagicMock()

# Expose the pipeline source directory on sys.path so test files can import
# ingest_data directly (it lives under src/kestra/files/ for Kestra consumption).
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "kestra" / "files"))


import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def mock_reverse_geocode():
    """Make reverse geocoding deterministic across tests."""
    fake_geo = {
        "country_code": "US",
        "country": "United States",
        "city": "Volcano",
        "state": "Hawaii",
        "population": 2575,
    }
    with patch("transformations.get_location_details", return_value=fake_geo):
        yield fake_geo


@pytest.fixture
def sample_earthquake_record():
    return {
        "type": "Feature",
        "properties": {
            "mag": 4.5,
            "place": "10km SSW of Volcano, Hawaii",
            "time": 1609459200000,
            "updated": 1609545600000,
            "type": "earthquake",
            "tsunami": 0,
            "felt": 10,
        },
        "geometry": {
            "type": "Point",
            "coordinates": [-155.233, 19.446, 5.0],
        },
        "id": "hv72783692",
    }


@pytest.fixture
def sample_record_no_geometry():
    return {
        "type": "Feature",
        "properties": {
            "mag": 2.0,
            "place": "Unknown",
            "time": 1609459200000,
            "updated": 1609545600000,
            "type": "earthquake",
            "tsunami": 0,
            "felt": None,
        },
        "id": "xx00000001",
    }
