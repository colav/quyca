from datetime import datetime
from typing import Generator

from domain.models.base_model import QueryParams, Affiliation, Author, ExternalId
from domain.models.work_model import Work, Source
from infrastructure.repositories import api_expert_repository
from domain.parsers import work_parser


def get_works_by_person(person_id: str, query_params: QueryParams) -> dict:
    works = api_expert_repository.get_works_by_person_for_api_expert(person_id, query_params)
    data = process_works(works)
    return {"data": data}


def get_works_by_affiliation(affiliation_id: str, query_params: QueryParams) -> dict:
    works = api_expert_repository.get_works_by_affiliation_for_api_expert(affiliation_id, query_params)
    data = process_works(works)
    return {"data": data}


def process_works(works: Generator) -> list:
    works_list = []
    for work in works:
        set_authors_data(work)
        set_authors_affiliations_data(work)
        set_source_data(work)
        works_list.append(work)
    data = work_parser.parse_api_expert(works_list)
    return data


def set_authors_data(work: Work) -> None:
    for author in work.authors:
        author_data = Author()
        if work.authors_data:
            author_data = next(filter(lambda x: x.id == author.id, work.authors_data), Author())
        author.external_ids = author_data.external_ids
        author.ranking = author_data.ranking
        author.last_names = author_data.last_names
        author.first_names = author_data.first_names
        author.sex = author_data.sex
        author.affiliations = author_data.affiliations
        if author_data.birthplace:
            author.birth_country = author_data.birthplace.country
        if author_data.birthdate and author_data.birthdate != -1 and author_data.birthdate != "":
            birthdate = datetime.fromtimestamp(author_data.birthdate)
            today = datetime.today()
            age = today.year - birthdate.year
            if (today.month, today.day) < (birthdate.month, birthdate.day):
                age -= 1
            author.age = age
    work.authors_data = None


def set_authors_affiliations_data(work: Work) -> None:
    for author in work.authors:
        author.countries = []
        for affiliation in author.affiliations:
            affiliation_data = Affiliation()
            if work.affiliations_data:
                affiliation_data = next(
                    filter(lambda x: x.hash == affiliation.hash, work.affiliations_data), Affiliation()
                )
            if affiliation_data.external_ids:
                affiliation.ror = next(
                    filter(lambda x: x.source == "ror", affiliation_data.external_ids), ExternalId()
                ).id
            if affiliation_data.addresses and (address := affiliation_data.addresses[0]):
                affiliation.geo.country = address.country
                affiliation.geo.country_code = address.country_code
                affiliation.geo.region = address.state
                affiliation.geo.city = address.city
                affiliation.geo.latitude = address.lat
                affiliation.geo.longitude = address.lng
                author.countries.append(affiliation.geo.country)
    work.affiliations_data = None


def set_source_data(work: Work) -> None:
    source_data = next(filter(lambda x: x.id == work.source.id, work.source_data), Source())
    work.source.types = source_data.types
    if source_data.external_ids:
        work.source.issn_l = next(filter(lambda x: x.source == "issn_l", source_data.external_ids), ExternalId()).id
    if source_data.updated:
        work.source.is_in_doaj = (
            True if next(filter(lambda x: x.source == "doaj", source_data.updated), None) else False
        )
    work.source_data = None
