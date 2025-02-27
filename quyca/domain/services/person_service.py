from domain.models.base_model import QueryParams
from domain.parsers import person_parser
from infrastructure.repositories import person_repository


def get_person_by_id(person_id: str) -> dict:
    person = person_repository.get_person_by_id(person_id)
    data = person_parser.parse_person(person)
    return {"data": data}


def search_persons(query_params: QueryParams) -> dict:
    pipeline_params = {
        "project": [
            "_id",
            "full_name",
            "affiliations",
            "external_ids",
            "citations_count",
            "products_count",
            "affiliations_data",
        ]
    }
    persons, total_results = person_repository.search_persons(query_params, pipeline_params)
    persons_list = []
    for person in persons:
        persons_list.append(person)
    data = person_parser.parse_search_result(persons_list)
    return {"data": data, "total_results": total_results}
