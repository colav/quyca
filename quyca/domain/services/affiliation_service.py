from domain.models.base_model import ExternalUrl, QueryParams
from domain.constants.institutions import institutions_list
from domain.parsers import affiliation_parser
from domain.models.affiliation_model import Affiliation, Relation
from infrastructure.repositories import (
    person_repository,
    affiliation_repository,
)


def get_affiliation_by_id(affiliation_id: str, affiliation_type: str) -> dict:
    affiliation = affiliation_repository.get_affiliation_by_id(affiliation_id)
    set_relation_external_urls(affiliation)
    set_upper_affiliations_and_logo(affiliation, affiliation_type)
    return {"data": affiliation.model_dump(by_alias=True)}


def get_related_affiliations_by_affiliation(affiliation_id: str, affiliation_type: str) -> dict:
    data = {}
    if affiliation_type == "institution":
        faculties = affiliation_repository.get_affiliations_by_institution(affiliation_id, "faculty")
        departments = affiliation_repository.get_affiliations_by_institution(affiliation_id, "department")
        groups = affiliation_repository.get_affiliations_by_institution(affiliation_id, "group")
        data["faculties"] = [faculty.model_dump(include={"id", "name"}) for faculty in faculties]
        data["departments"] = [department.model_dump(include={"id", "name"}) for department in departments]
        data["groups"] = [group.model_dump(include={"id", "name"}) for group in groups]
        if len(data["faculties"]) == 0 and len(data["departments"]) == 0:
            authors = person_repository.get_persons_by_affiliation(affiliation_id)
            data["authors"] = [author.model_dump(include={"id", "full_name"}) for author in authors]

    elif affiliation_type == "faculty":
        departments = affiliation_repository.get_departments_by_faculty(affiliation_id)
        groups = affiliation_repository.get_groups_by_faculty_or_department(affiliation_id)
        authors = person_repository.get_persons_by_affiliation(affiliation_id)
        data["departments"] = [department.model_dump(include={"id", "name"}) for department in departments]
        data["groups"] = [group.model_dump(include={"id", "name"}) for group in groups]
        data["authors"] = [author.model_dump(include={"id", "full_name"}) for author in authors]
    elif affiliation_type == "department":
        groups = affiliation_repository.get_groups_by_faculty_or_department(affiliation_id)
        authors = person_repository.get_persons_by_affiliation(affiliation_id)
        data["groups"] = [group.model_dump(include={"id", "name"}) for group in groups]
        data["authors"] = [author.model_dump(include={"id", "full_name"}) for author in authors]
    elif affiliation_type == "group":
        authors = person_repository.get_persons_by_affiliation(affiliation_id)
        data["authors"] = [author.model_dump(include={"id", "full_name"}) for author in authors]
    return data


def search_affiliations(affiliation_type: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "project": [
            "_id",
            "names",
            "addresses.country_code",
            "external_ids",
            "external_urls",
            "relations",
            "types",
            "citations_count",
            "products_count",
            "relations_data",
        ]
    }
    affiliations, total_results = affiliation_repository.search_affiliations(
        affiliation_type, query_params, pipeline_params
    )
    affiliations_list = []
    for affiliation in affiliations:
        set_relation_external_urls(affiliation)
        set_upper_affiliations_and_logo(affiliation, affiliation_type)
        affiliations_list.append(affiliation)
    data = affiliation_parser.parse_search_result(affiliations_list)
    return {"data": data, "total_results": total_results}


def set_relation_external_urls(affiliation: Affiliation) -> None:
    for relation in affiliation.relations:
        relation_data = next(
            filter(lambda x: x.id == relation.id, affiliation.relations_data),
            Relation(),
        )
        relation.external_urls = relation_data.external_urls


def set_upper_affiliations_and_logo(affiliation: Affiliation, affiliation_type: str) -> None:
    if affiliation_type == "institution":
        affiliation.logo = next(
            filter(lambda x: x.source == "logo", affiliation.external_urls),
            ExternalUrl(),
        ).url
    upper_affiliations = []
    for relation in affiliation.relations:
        if affiliation_type == "faculty" and relation.types[0].type in institutions_list:
            set_logo(affiliation, relation)
            upper_affiliations.append(relation)
        elif affiliation_type == "department" and relation.types[0].type in institutions_list + ["faculty"]:
            set_logo(affiliation, relation)
            upper_affiliations.append(relation)
        elif affiliation_type == "group" and relation.types[0].type in institutions_list + [
            "department",
            "faculty",
        ]:
            set_logo(affiliation, relation)
            upper_affiliations.append(relation)
    affiliation.affiliations = upper_affiliations


def set_logo(affiliation: Affiliation, relation: Relation) -> None:
    if relation.types[0].type in institutions_list:
        affiliation.logo = next(filter(lambda x: x.source == "logo", relation.external_urls), ExternalUrl()).url
