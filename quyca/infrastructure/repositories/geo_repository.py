from typing import Any, Iterator

from quyca.domain.models.base_model import QueryParams
from quyca.infrastructure.mongo import database
from quyca.infrastructure.repositories import base_repository

VALID_LOCATION_TYPES = {"states": "state", "cities": "city"}


def search_geolocations(query_params: QueryParams, location_type: str) -> tuple[Iterator[dict[str, Any]], int]:
    """
    Busca los states o cities distintos (Colombia) según location_type.
    """
    if location_type not in VALID_LOCATION_TYPES:
        raise ValueError(f"location_type inválido: {location_type}. Debe ser 'states' o 'cities'.")

    address_field = VALID_LOCATION_TYPES[location_type]

    pipeline: list[dict[str, Any]] = []

    if query_params.keywords:
        pipeline.append({"$match": {"$text": {"$search": query_params.keywords}}})

    pipeline.append({"$match": {"addresses.country": "Colombia"}})
    pipeline.append({"$unwind": "$addresses"})
    pipeline.append({"$match": {"addresses.country": "Colombia"}})

    pipeline.append({"$group": {"_id": f"$addresses.{address_field}"}})
    pipeline.append({"$match": {"_id": {"$nin": [None, ""]}}})

    data_stage: list[dict[str, Any]] = [{"$sort": {"_id": 1}}]
    base_repository.set_pagination(data_stage, query_params)

    pipeline.append(
        {
            "$facet": {
                "data": data_stage,
                "metadata": [{"$count": "total"}],
            }
        }
    )

    result: dict[str, Any] = next(
        database["affiliations"].aggregate(pipeline),
        {"data": [], "metadata": []},
    )

    geolocations = iter(result["data"])
    total_geolocations = result["metadata"][0]["total"] if result["metadata"] else 0

    return geolocations, total_geolocations
