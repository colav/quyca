from quyca.domain.models.base_model import QueryParams
from quyca.domain.parsers import geo_parser
from quyca.infrastructure.repositories import geo_repository


def search_geolocation(query_params: QueryParams, location_type: str) -> dict:
    """
    Searches for geolocation data based on the provided query parameters and location type.

    Parameters:
    -----------
    query_params : QueryParams
        The query parameters to filter the geolocation data.
    location_type : str
        The type of location to search for (e.g., "state", "city").

    Returns:
    --------
    dict
        A dictionary containing the search data and the total number of results.
    """
    geolocations, total_geolocations = geo_repository.search_geolocations(query_params, location_type)
    geolocation_list = list(geolocations)

    data = geo_parser.parse_search_result(geolocation_list)

    return {"data": data, "total_results": total_geolocations}
