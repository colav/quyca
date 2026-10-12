import time

from quyca.domain.models.base_model import QueryParams
from quyca.domain.parsers.api_expert_parser import build_metadata, parse_fields
from quyca.domain.parsers.person import person_parser
from quyca.infrastructure.repositories import api_expert_repository
from quyca.infrastructure.repositories.person import person_repository


def get_person_by_id(person_id: str) -> dict:
    pipeline_params = build_person_api_pipeline_params()
    person = person_repository.get_person_by_id(person_id, pipeline_params)
    data = person_parser.parse_person_api(person)
    return {"data": data}


def get_works_by_person(person_id: str, query_params: QueryParams, current_url: str) -> dict:
    start_time = time.time()
    fields = parse_fields(query_params.fields)
    pipeline_params = {"project": fields} if fields else {}
    works = api_expert_repository.get_works_by_person_for_api_expert(person_id, query_params, pipeline_params)
    total_count = api_expert_repository.count_works_by_person_for_api_expert(person_id, query_params)
    return build_metadata(works, total_count, query_params, start_time, current_url)


def build_person_api_pipeline_params() -> dict:
    pipeline_params = {
        "project": [
            "_id",
            "full_name",
            "first_names",
            "h5_index",
            "h_index",
            "last_names",
            "initials",
            "affiliations",
            "external_ids",
            "citations_count",
            "products_count",
            "age",
            "degrees",
            "updated",
            "sex",
            "subjects",
            "ranking",
        ]
    }
    return pipeline_params
