from typing import Generator, Tuple

from bson import ObjectId

from infrastructure.generators import project_generator
from domain.models.base_model import QueryParams
from domain.models.project_model import Project
from infrastructure.repositories import base_repository
from infrastructure.mongo import database
from domain.exceptions.not_entity_exception import NotEntityException


def get_project_by_id(project_id: str) -> Project:
    project = database["projects"].find_one(ObjectId(project_id))
    if not project:
        raise NotEntityException(f"The project with id {project_id} does not exist.")
    return Project(**project)


def get_projects_by_affiliation(
    affiliation_id: str,
    query_params: QueryParams,
    pipeline_params: dict | None = None,
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {
            "$match": {
                "authors.affiliations.id": affiliation_id,
            },
        },
    ]
    if sort := query_params.sort:
        base_repository.set_sort(sort, pipeline)
    base_repository.set_pagination(pipeline, query_params)
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    cursor = database["projects"].aggregate(pipeline)
    return project_generator.get(cursor)


def get_projects_count_by_affiliation(affiliation_id: str) -> int:
    pipeline = get_projects_by_affiliation_pipeline(affiliation_id)
    pipeline += [{"$count": "total"}]
    return next(database["projects"].aggregate(pipeline), {"total": 0}).get("total", 0)


def get_projects_by_person(person_id: str, query_params: QueryParams, pipeline_params: dict | None = None) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {"$match": {"authors.id": person_id}},
    ]
    if sort := query_params.sort:
        base_repository.set_sort(sort, pipeline)
    base_repository.set_pagination(pipeline, query_params)
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    cursor = database["projects"].aggregate(pipeline)
    return project_generator.get(cursor)


def get_projects_count_by_person(person_id: str) -> int:
    pipeline = [{"$match": {"authors.id": person_id}}, {"$count": "total"}]
    return next(database["projects"].aggregate(pipeline), {"total": 0}).get("total", 0)


def search_projects(query_params: QueryParams, pipeline_params: dict | None = None) -> Tuple[Generator, int]:
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    projects = database["projects"].aggregate(pipeline)
    count_pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    count_pipeline += [
        {"$count": "total_results"},  # type: ignore
    ]
    total_results = next(database["projects"].aggregate(count_pipeline), {"total_results": 0}).get("total_results", 0)
    return project_generator.get(projects), total_results


def get_projects_by_affiliation_pipeline(affiliation_id: str) -> list:
    return [
        {
            "$match": {
                "authors.affiliations.id": affiliation_id,
            },
        },
    ]
