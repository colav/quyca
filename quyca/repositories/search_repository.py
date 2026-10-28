from typing import Any, Dict, Generator, List
from quyca.generators import (
    affiliation_generator,
    geo_generator,
    patent_generator,
    person_generator,
    project_generator,
    source_generator,
    work_generator,
)
from quyca.models.base_model import QueryParams
from quyca.clients.mongo import database
from quyca.constants.institutions import institutions_list
from quyca.repositories import base_repository
from quyca.repositories import search_affiliation_filters_repository, search_source_filters_repository
from quyca.repositories import work_repository


def search_persons(query_params: QueryParams, pipeline_params: Dict | None = None) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    cursor = database["person"].aggregate(pipeline)
    return person_generator.get(cursor)


def search_count_persons(query_params: QueryParams, pipeline_params: Dict | None = None) -> int:
    if pipeline_params is None:
        pipeline_params = {}
    count_pipeline: list[dict[str, Any]] = (
        [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    )
    count_pipeline += [{"$count": "total_results"}]
    result = next(database["person"].aggregate(count_pipeline), {"total_results": 0})
    return int(result.get("total_results", 0))


def search_works(query_params: QueryParams, pipeline_params: Dict | None = None) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline: List[Dict[str, Any]] = []
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    work_repository.set_product_filters(pipeline, query_params)
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    work_repository.set_issn_to_pipeline(pipeline)
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def search_count_works(query_params: QueryParams) -> int:
    query_dict = query_params.model_dump(exclude_none=True)
    base_params = {"page", "limit", "sort"}
    is_full_scan = set(query_dict.keys()).issubset(base_params)
    if is_full_scan:
        return int(database["works"].estimated_document_count())
    count_pipeline: list[dict[str, Any]] = (
        [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    )
    work_repository.set_product_filters(count_pipeline, query_params)
    count_pipeline.append({"$count": "total_count"})
    result = next(database["works"].aggregate(count_pipeline), {"total_count": 0})
    return int(result.get("total_count", 0))


def search_affiliations(
    affiliation_type: str, query_params: QueryParams, pipeline_params: Dict | None = None
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    types = institutions_list if affiliation_type == "institution" else [affiliation_type]
    pipeline: List[Dict[str, Any]] = []
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    pipeline.append({"$match": {"types.type": {"$in": types}}})

    search_affiliation_filters_repository.set_affiliation_filters(pipeline, query_params)
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    cursor = database["affiliations"].aggregate(pipeline)
    return affiliation_generator.get(cursor)


def search_count_affiliations(query_params: QueryParams, affiliation_type: str) -> int:
    types = institutions_list if affiliation_type == "institution" else [affiliation_type]
    count_pipeline: list[dict[str, Any]] = []
    count_pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    count_pipeline.append({"$match": {"types.type": {"$in": types}}})
    search_affiliation_filters_repository.set_affiliation_filters(count_pipeline, query_params)
    count_pipeline.append({"$count": "total_count"})
    result = next(database["affiliations"].aggregate(count_pipeline), {"total_count": 0})
    return int(result.get("total_count", 0))


def search_sources(query_params: QueryParams, pipeline_params: Dict | None = None) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline: List[Dict[str, Any]] = []
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    search_source_filters_repository.set_source_filters(pipeline, query_params)
    search_source_filters_repository.set_source_type_pipeline(pipeline)
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    cursor = database["sources"].aggregate(pipeline)
    return source_generator.get(cursor)


def search_count_sources(query_params: QueryParams) -> int:
    count_pipeline: list[dict[str, Any]] = []
    count_pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    search_source_filters_repository.set_source_filters(count_pipeline, query_params)
    count_pipeline.append({"$count": "total_count"})
    result = next(database["sources"].aggregate(count_pipeline), {"total_count": 0})
    return int(result.get("total_count", 0))


def search_patents(query_params: QueryParams, pipeline_params: Dict | None = None) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline: List[Dict[str, Any]] = []
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    cursor = database["patents"].aggregate(pipeline)
    return patent_generator.get(cursor)


def search_count_patents(query_params: QueryParams) -> int:
    count_pipeline: list[dict[str, Any]] = []
    count_pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    count_pipeline.append({"$count": "total_count"})
    result = next(database["patents"].aggregate(count_pipeline), {"total_count": 0})
    return int(result.get("total_count", 0))


def search_projects(query_params: QueryParams, pipeline_params: Dict | None = None) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline: List[Dict[str, Any]] = []
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    cursor = database["projects"].aggregate(pipeline)
    return project_generator.get(cursor)


def search_count_projects(query_params: QueryParams) -> int:
    count_pipeline: list[dict[str, Any]] = []
    count_pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    count_pipeline.append({"$count": "total_count"})
    result = next(database["projects"].aggregate(count_pipeline), {"total_count": 0})
    return int(result.get("total_count", 0))


def search_geo(query_params: QueryParams, geo_type: str, pipeline_params: Dict | None = None) -> Generator:
    if pipeline_params is None:
        pipeline_params = {"collection": "geo"}
    pipeline: List[Dict[str, Any]] = (
        [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    )
    pipeline.append({"$match": {"type": geo_type}})
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    cursor = database["geo"].aggregate(pipeline)
    return geo_generator.get(cursor)


def search_count_geo(query_params: QueryParams, geo_type: str) -> int:
    count_pipeline: list[dict[str, Any]] = [{"$match": {"type": geo_type}}]
    count_pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    count_pipeline.append({"$count": "total_count"})
    result = next(database["geo"].aggregate(count_pipeline), {"total_count": 0})
    return int(result.get("total_count", 0))
