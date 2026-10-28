from typing import Any, Dict, Generator, List

from bson import ObjectId

from quyca.models.base_model import QueryParams
from quyca.models.project_model import Project
from quyca.constants.institutions import institutions_list
from quyca.generators import project_generator
from quyca.clients.mongo import database
from quyca.exceptions.not_entity_exception import NotEntityException
from quyca.repositories import base_repository


def get_project_by_id(project_id: str) -> Project:
    project = database["projects"].find_one({"_id": ObjectId(project_id)})
    if not project:
        raise NotEntityException(f"The project with id {project_id} does not exist.")
    return Project(**project)


def get_projects_by_affiliation(
    affiliation_id: str,
    affiliation_type: str,
    query_params: QueryParams,
    pipeline_params: dict | None = None,
) -> Generator:
    types = institutions_list if affiliation_type == "institution" else [affiliation_type]
    if pipeline_params is None:
        pipeline_params = {}
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"authors.affiliations.id": affiliation_id}},
        {"$match": {"authors.affiliations.types.type": {"$in": types}}},
    ]
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    cursor = database["projects"].aggregate(pipeline)
    return project_generator.get(cursor)


def get_projects_count_by_affiliation(affiliation_id: str) -> int:
    pipeline: List[Dict[str, Any]] = [{"$match": {"authors.affiliations.id": affiliation_id}}, {"$count": "total"}]
    return next(database["projects"].aggregate(pipeline), {"total": 0}).get("total", 0)


def get_projects_by_person(person_id: str, query_params: QueryParams, pipeline_params: dict | None = None) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {"$match": {"authors.id": person_id}},
    ]
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    cursor = database["projects"].aggregate(pipeline)
    return project_generator.get(cursor)


def get_projects_count_by_person(person_id: str) -> int:
    pipeline: List[Dict[str, Any]] = [{"$match": {"authors.id": person_id}}, {"$count": "total"}]
    result = next(database["projects"].aggregate(pipeline), {"total": 0})
    return result.get("total", 0)
