from quyca.infrastructure.repositories.geo import geo_repository


def geo_by_id(geo_type: str, geo_id: str) -> dict:
    pipeline_params = build_geo_pipeline_params()
    geo = geo_repository.get_geolocation_by_id(geo_type, geo_id, pipeline_params)
    return {"data": geo.model_dump(exclude_none=True)}


def related_affiliations_by_geo(geo_type: str, geo_id: str) -> dict:
    geo = geo_repository.get_geo_affiliations(geo_type, geo_id)
    data = {
        "institutions": [institution.model_dump() for institution in geo.institutions or []],
        "groups": [group.model_dump() for group in geo.groups or []],
    }
    if geo_type == "states":
        data["cities"] = [city.model_dump() for city in geo.cities or []]
    return data


def build_geo_pipeline_params() -> dict:
    pipeline_params = {
        "project": [
            "id",
            "name",
            "state",
            "country",
            "country_code",
            "latitude",
            "longitude",
            "external_ids",
            "citations_count",
            "products_count",
            "authors_count",
            "institutions_count",
            "groups_count",
            "cities_count",
        ],
        "collection": "geo",
    }
    return pipeline_params
