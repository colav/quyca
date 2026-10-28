from quyca.parsers import person_parser
from quyca.repositories import person_repository


def get_person_by_id(person_id: str) -> dict:
    pipeline_params = {
        "project": [
            "_id",
            "full_name",
            "affiliations",
            "external_ids",
            "citations_count",
            "products_count",
            "affiliations_data",
            "logo",
            "h_index",
            "h5_index",
        ]
    }
    person = person_repository.get_person_by_id(person_id, pipeline_params)
    data = person_parser.parse_person(person)
    return {"data": data}
