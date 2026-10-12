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
