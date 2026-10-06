from quyca.domain.parsers.person import person_parser
from quyca.infrastructure.repositories.person import person_repository
from quyca.domain.services.base_service import build_person_pipeline_params


def get_person_by_id(person_id: str) -> dict:
    pipeline_params = build_person_pipeline_params()
    person = person_repository.get_person_by_id(person_id, pipeline_params)
    data = person_parser.parse_person(person)
    return {"data": data}
