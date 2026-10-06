from quyca.domain.models.person_model import Person


def parse_person(person: Person) -> dict:
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


def parse_person_api(person: Person) -> dict:
    include = [
        "id",
        "full_name",
        "first_names",
        "last_names",
        "initials",
        "affiliations",
        "external_ids",
        "products_count",
        "citations_count",
        "logo",
        "h_index",
        "h5_index",
        "age",
        "degrees",
        "updated",
        "sex",
        "subjects",
        "ranking",
    ]
    return person.model_dump(include=set(include), exclude_none=True)
