from quyca.domain.models.person_model import Person


def parse_search_result(persons: list) -> list:
    include = [
        "id",
        "full_name",
        "affiliations",
        "external_ids",
        "products_count",
        "citations_count",
        "logo",
        "h_index",
        "h5_index",
    ]
    return [person.model_dump(include=include) for person in persons]


def parse_person(person: Person, include: list = []) -> dict:
    if not include:
        include = [
            "id",
            "full_name",
            "affiliations",
            "external_ids",
            "products_count",
            "citations_count",
            "logo",
            "h_index",
            "h5_index",
        ]
    return person.model_dump(include=set(include), exclude_none=True)
