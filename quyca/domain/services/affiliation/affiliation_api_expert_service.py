import time

from quyca.domain.models.base_model import QueryParams
from quyca.domain.parsers.api_expert_parser import build_metadata
from quyca.infrastructure.repositories import api_expert_repository


def get_works_by_affiliation(
    affiliation_id: str, query_params: QueryParams, affiliation_type: str, current_url: str
) -> dict:
    start_time = time.time()

    if affiliation_type == "institution":
        affiliation_type = "education"

    works = api_expert_repository.get_works_by_affiliation_for_api_expert(
        affiliation_id, query_params, affiliation_type
    )
    total_count = api_expert_repository.count_works_by_affiliation_for_api_expert(
        affiliation_id, query_params, affiliation_type
    )
    return build_metadata(works, total_count, query_params, start_time, current_url)
