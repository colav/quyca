from typing import Any, Dict, Generator, List

from bson import ObjectId


from quyca.domain.models.base_model import QueryParams
from quyca.infrastructure.generators import work_generator
from quyca.infrastructure.mongo import database
from quyca.infrastructure.repositories import base_repository, work_repository


def get_works_csv_by_person(person_id: str, query_params: QueryParams, pipeline_params: dict) -> Generator:
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"authors.id": person_id}},
    ]
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    work_repository.set_product_filters(pipeline, query_params)
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_csv_by_affiliation(
    affiliation_id: str, query_params: QueryParams, affiliation_type: str, pipeline_params: dict
) -> Generator:
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"authors.affiliations.id": affiliation_id, "authors.affiliations.types.type": affiliation_type}},
    ]
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    work_repository.set_product_filters(pipeline, query_params)
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_csv_by_source(source_id: str, query_params: QueryParams, pipeline_params: dict) -> Generator:
    """
    Query database for works from a specific source using MongoDB aggregation.

    Builds and executes a MongoDB aggregation pipeline that:
    1. Filters works by source ID
    2. Projects only necessary fields (from pipeline_params)
    3. Applies additional filters from query_params (dates, types, etc.)
    4. Returns results as a generator

    Args:
        source_id: Source identifier to filter works
        query_params: Additional filters (pagination, date ranges, etc.)
        pipeline_params: Projection parameters defining which fields to retrieve

    Returns:
        Generator: Generator yielding Work objects from database cursor

    Note:
        Uses generator to avoid loading all works into memory at once,
        which is critical for sources with thousands of publications
    """
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"source.id": ObjectId(source_id)}},
    ]
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    work_repository.set_product_filters(pipeline, query_params)
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)
