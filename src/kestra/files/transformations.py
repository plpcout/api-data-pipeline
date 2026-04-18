from typing import Dict, Optional

import pendulum
import reverse_geocode as rg


def get_location_details(latitude: float, longitude: float) -> Dict[str, Optional[str]]:
    """Reverse geocode coordinates into country/state/city metadata."""
    geo_details = rg.get((latitude, longitude))
    return {
        "country_code": geo_details.get("country_code", None),
        "country": geo_details.get("country", None),
        "city": geo_details.get("city", None),
        "population": geo_details.get("population", None),
        "state": geo_details.get("state", None),
    }


def convert_timestamp_to_iso(timestamp: int) -> str:
    """Convert a millisecond Unix timestamp into an ISO 8601 string (UTC)."""
    return (
        pendulum.from_timestamp(timestamp / 1000, tz="UTC")
        .replace(microsecond=0)
        .to_iso8601_string()
    )


def process_earthquake_record(record: Dict) -> Optional[Dict]:
    """Flatten geometry, convert timestamps, and enrich with reverse-geocoded location.

    Returns None when the record is missing geometry (cannot be processed downstream).
    """
    record["properties"]["time"] = convert_timestamp_to_iso(record["properties"]["time"])
    record["properties"]["updated"] = convert_timestamp_to_iso(record["properties"]["updated"])

    if "geometry" not in record:
        return None

    record["properties"]["g_type"] = record["geometry"]["type"]
    coordinates = record["geometry"]["coordinates"]
    longitude, latitude, depth = coordinates[0], coordinates[1], coordinates[2]
    record["properties"]["g_longitude"] = longitude
    record["properties"]["g_latitude"] = latitude
    record["properties"]["g_depth"] = depth

    geo_details = get_location_details(latitude, longitude)
    record["properties"]["country_code"] = geo_details["country_code"]
    record["properties"]["country"] = geo_details["country"]
    record["properties"]["state"] = geo_details["state"]
    record["properties"]["city"] = geo_details["city"]
    record["properties"]["population"] = geo_details["population"]

    del record["geometry"]
    return record
