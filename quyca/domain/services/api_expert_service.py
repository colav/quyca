import time
from typing import Generator

from quyca.domain.models.base_model import QueryParams
from quyca.infrastructure.repositories import api_expert_repository
from quyca.domain.parsers import work_parser


def get_works_by_person(person_id: str, query_params: QueryParams) -> dict:
    start_time = time.time()
    works = api_expert_repository.get_works_by_person_for_api_expert(person_id, query_params)
    total_count = api_expert_repository.count_works_by_person_for_api_expert(person_id, query_params)
    return build_metadata(works, total_count, query_params, start_time)


def get_works_by_affiliation(affiliation_id: str, query_params: QueryParams, affiliation_type: str) -> dict:
    start_time = time.time()

    if affiliation_type == "institution":
        affiliation_type = "Education"

    works = api_expert_repository.get_works_by_affiliation_for_api_expert(
        affiliation_id, query_params, affiliation_type
    )
    total_count = api_expert_repository.count_works_by_affiliation_for_api_expert(
        affiliation_id, query_params, affiliation_type
    )
    return build_metadata(works, total_count, query_params, start_time)


def get_works_by_source(source_id: str, query_params: QueryParams) -> dict:
    start_time = time.time()
    works = api_expert_repository.get_works_by_source_for_api_expert(source_id, query_params)
    total_count = api_expert_repository.count_works_by_source_for_api_expert(source_id, query_params)
    return build_metadata(works, total_count, query_params, start_time)


def search_works(query_params: QueryParams) -> dict:
    start_time = time.time()
    works = api_expert_repository.search_works_for_api_expert(query_params)
    total_count = api_expert_repository.count_works_for_api_expert(query_params)
    return build_metadata(works, total_count, query_params, start_time)


def build_metadata(works: Generator, total_count: int, query_params: QueryParams, start_time: float) -> dict:
    """
    This function builds the metadata for the API expert response.
    """
    db_response_time_ms = int((time.time() - start_time) * 1000)
    data = process_works(works)

    meta = {
        "count": total_count,
        "db_response_time_ms": db_response_time_ms,
        "page": query_params.page or 1,
        "size": query_params.limit or len(data),
    }

    return {"meta": meta, "data": data}


def process_works(works: Generator) -> list:
    works_list = list(works)
    data = work_parser.parse_api_expert(works_list)
    return data
