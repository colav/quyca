import time

from quyca.domain.models.base_model import QueryParams
from quyca.domain.parsers.api_expert_parser import build_metadata, parse_fields
from quyca.infrastructure.repositories import api_expert_repository


def get_works_by_geo(geo_type: str, geo_id: str, query_params: QueryParams, current_url: str) -> dict:
    start_time = time.time()
    fields = parse_fields(query_params.fields)
    pipeline_params = {"project": fields} if fields else {}
    works = api_expert_repository.get_works_by_geo_for_api_expert(geo_type, geo_id, query_params, pipeline_params)
    total_count = api_expert_repository.count_works_by_geo_for_api_expert(geo_type, geo_id, query_params)
    return build_metadata(works, total_count, query_params, start_time, current_url)
