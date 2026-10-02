from typing import Any, List, Dict

from quyca.domain.constants.geo_states_cities import GEO_RELATED_FIELDS
from quyca.domain.exceptions.not_entity_exception import NotEntityException
from quyca.domain.models.geo_model import Geo
from quyca.infrastructure.generators import geo_generator
from quyca.infrastructure.mongo import database


def get_geolocation_by_id(geo_type: str, geo_id: str, pipeline_params: Dict[str, Any]) -> Geo:
    project = {"_id": 1, **{field: 1 for field in pipeline_params.get("project") or []}}
    return get_geo(geo_type, geo_id, {"$project": project})


def build_works_geo_match(geo_type: str, geo_id: str) -> Dict[str, Any]:
    return {"$match": {"authors.affiliations.id": {"$in": get_geo_institution_ids(geo_type, geo_id)}}}


def get_geo_institution_ids(geo_type: str, geo_id: str) -> List[str]:
    geo = get_geo(geo_type, geo_id, {"$project": {"institutions.id": 1}})
    return [institution.id for institution in geo.institutions or []]


def get_geo_affiliations(geo_type: str, geo_id: str) -> Geo:
    return get_geo(geo_type, geo_id, {"$project": GEO_RELATED_FIELDS})


def get_geo(geo_type: str, geo_id: str, project_stage: Dict[str, Any]) -> Geo:
    pipeline: List[Dict[str, Any]] = [{"$match": {"_id": geo_id, "type": geo_type}}, project_stage]
    geo = next(geo_generator.get(database["geo"].aggregate(pipeline)), None)
    if geo is None:
        raise NotEntityException(f"The geolocation with id {geo_id} does not exist.")
    return geo
