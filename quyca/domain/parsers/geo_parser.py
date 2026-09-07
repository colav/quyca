from typing import Any


def parse_search_result(geolocations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Parses the search result of geolocations.
    """
    data = []
    for geolocation in geolocations:
        data.append({"geoname": geolocation["_id"]})

    return data
