from quyca.repositories import geo_repository


def get_geo_by_id(geo_type: str, geo_id: str) -> dict:
    geo = geo_repository.get_geo_by_id(geo_type, geo_id)
    return {"data": geo.model_dump(exclude_none=True)}


def get_related_affiliations_by_geo(geo_type: str, geo_id: str) -> dict:
    geo = geo_repository.get_geo_affiliations(geo_type, geo_id)
    data = {
        "institutions": [institution.model_dump() for institution in geo.institutions or []],
        "groups": [group.model_dump() for group in geo.groups or []],
    }
    if geo_type == "states":
        data["cities"] = [city.model_dump() for city in geo.cities or []]
    return data
