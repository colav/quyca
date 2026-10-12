from quyca.domain.models.person_model import Person


def parse_person(person: Person) -> dict:
    exclude = ["birthdate"]
    return person.model_dump(exclude=set(exclude), exclude_none=True)
