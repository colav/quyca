import time

from quyca.domain.models.base_model import QueryParams
from quyca.domain.parsers.api_expert_parser import build_metadata
from quyca.infrastructure.repositories import api_expert_repository


def get_work_by_id(work_id: str, query_params: QueryParams, current_url: str) -> dict:
    start_time = time.time()
    work = api_expert_repository.get_work_by_id_for_api_expert(work_id)
    return build_metadata(work, 1, query_params, start_time, current_url)


def get_work_by_doi(work_doi: str, query_params: QueryParams, current_url: str) -> dict:
    start_time = time.time()
    work = api_expert_repository.get_work_by_doi_for_api_expert(work_doi)
    return build_metadata(work, 1, query_params, start_time, current_url)


def get_works_by_person(person_id: str, query_params: QueryParams, current_url: str) -> dict:
    start_time = time.time()
    works = api_expert_repository.get_works_by_person_for_api_expert(person_id, query_params)
    total_count = api_expert_repository.count_works_by_person_for_api_expert(person_id, query_params)
    return build_metadata(works, total_count, query_params, start_time, current_url)
