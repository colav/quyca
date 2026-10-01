from quyca.domain.parsers.person import person_parser
from quyca.infrastructure.repositories.person import person_repository


def get_person_by_id(person_id: str) -> dict:
    pipeline_params = build_person_api_pipeline_params()
    person = person_repository.get_person_by_id(person_id, pipeline_params)
    data = person_parser.parse_person(person)
    return {"data": data}


def build_person_api_pipeline_params() -> dict:
    pipeline_params = {
        "project": [
            "_id",
            "full_name",
            "first_names",
            "last_names",
            "initials",
            "affiliations",
            "external_ids",
            "citations_count",
            "products_count",
            "affiliations_data",
            "age",
            "degrees",
            "updated",
            "sex",
            "subjects",
            "ranking",
            "birthdate",
        ]
    }
    return pipeline_params
