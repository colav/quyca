from datetime import datetime
from urllib.parse import urlparse

from database.models.base_model import ExternalUrl, ExternalId
from database.models.work_model import Work, Title, ProductType
from database.repositories import person_repository, affiliation_repository
from database.repositories import work_repository
from enums.external_urls import external_urls
from enums.institutions import institutions_list
from services import new_source_service
from services.parsers import work_parser


def get_work_by_id(work_id: str):
    work = work_repository.get_work_by_id(work_id)
    set_external_ids(work)
    set_external_urls(work)
    if work.authors:
        limit_authors(work)
        set_authors_external_ids(work)
    if work.bibliographic_info:
        set_bibliographic_info(work)
    if work.source.id:
        new_source_service.update_work_source(work)
    if work.titles:
        set_title_and_language(work)
    if work.types:
        set_product_types(work)
    return work


def get_works_csv_by_affiliation(affiliation_id: str, affiliation_type: str) -> str:
    if affiliation_type == "institution":
        works = work_repository.get_csv_works_by_institution(affiliation_id)
    else:
        works = work_repository.get_works_by_affiliation(
            affiliation_id, affiliation_type
        )
    data = get_csv_data(works)
    return work_parser.parse_csv(data)


def get_works_csv_by_person(person_id: str) -> str:
    works = work_repository.get_works_by_person(person_id)
    data = get_csv_data(works)
    return work_parser.parse_csv(data)


def get_csv_data(works):
    data = []
    for work in works:
        set_doi(work)
        set_csv_affiliations(work)
        set_csv_authors(work)
        set_csv_bibliographic_info(work)
        set_csv_citations_count(work)
        set_csv_subjects(work)
        set_csv_titles(work)
        set_csv_types(work)
        new_source_service.update_csv_work_source(work)
        set_csv_date_published(work)
        data.append(work)
    return data


def set_csv_date_published(work: Work):
    work.date_published = datetime.fromtimestamp(work.date_published).strftime(
        "%d-%m-%Y"
    )


def set_doi(work: Work):
    work.doi = next(
        filter(lambda external_id: external_id.source == "doi", work.external_ids),
        ExternalId(),
    ).id


def set_csv_types(work: Work):
    openalex_types = []
    scienti_types = []
    for work_type in work.types:
        if work_type.source == "openalex":
            openalex_types.append(str(work_type.type))
        elif work_type.source == "scienti":
            scienti_types.append(work_type.type)
    work.openalex_types = " | ".join(set(openalex_types))
    work.scienti_types = " | ".join(set(scienti_types))


def set_csv_titles(work: Work):
    titles = []
    for title in work.titles:
        titles.append(str(title.title) + " / " + str(title.lang))
    work.titles = " | ".join(set(titles))


def set_csv_subjects(work: Work):
    if work.subjects:
        subjects = []
        for subject in work.subjects[0].subjects:
            subjects.append(str(subject.name))
        work.subjects = " | ".join(set(subjects))


def set_csv_citations_count(work: Work):
    for citation_count in work.citations_count:
        if citation_count.source == "openalex":
            work.openalex_citations_count = str(citation_count.count)
        elif citation_count.source == "scholar":
            work.scholar_citations_count = str(citation_count.count)


def set_csv_bibliographic_info(work: Work):
    work.issue = work.bibliographic_info.issue
    work.is_open_access = work.bibliographic_info.is_open_access
    work.open_access_status = work.bibliographic_info.open_access_status
    work.start_page = work.bibliographic_info.start_page
    work.end_page = work.bibliographic_info.end_page
    work.volume = work.bibliographic_info.volume


def set_csv_authors(work: Work):
    authors = []
    for author in work.authors:
        authors.append(str(author.full_name))
    work.authors = " | ".join(set(authors))


def set_csv_affiliations(work: Work):
    institutions = []
    departments = []
    faculties = []
    groups = []
    groups_ranking = []
    for author in work.authors:
        for affiliation in author.affiliations:
            affiliation_data = next(
                filter(lambda x: x.id == affiliation.id, work.affiliations_data)
            )
            if affiliation.types[0].type in institutions_list:
                institutions.append(
                    str(affiliation.name)
                    + " / "
                    + str(affiliation_data.addresses[0].country)
                )
            elif affiliation.types[0].type == "department":
                departments.append(
                    str(affiliation.name)
                    + " / "
                    + str(affiliation_data.addresses[0].country)
                )
            elif affiliation.types[0].type == "faculty":
                faculties.append(
                    str(affiliation.name)
                    + " / "
                    + str(affiliation_data.addresses[0].country)
                )
            elif affiliation.types[0].type == "group":
                groups.append(
                    str(affiliation.name)
                    + " / "
                    + str(affiliation_data.addresses[0].country)
                )
                ranking = affiliation_data.ranking[0]
                if type(ranking.date) == int:
                    groups_ranking.append(
                        str(ranking.rank)
                        + str(ranking.order)
                        + " / "
                        + datetime.fromtimestamp(ranking.date).strftime("%d-%m-%Y")
                    )
    work.institutions = " | ".join(set(institutions))
    work.departments = " | ".join(set(departments))
    work.faculties = " | ".join(set(faculties))
    work.groups = " | ".join(set(groups))
    work.groups_ranking = " | ".join(set(groups_ranking))


def set_title_and_language(work: Work):
    def order(title: Title):
        hierarchy = ["openalex", "scholar", "scienti", "minciencias", "ranking"]
        return (
            hierarchy.index(title.source) if title.source in hierarchy else float("inf")
        )

    first_title = sorted(work.titles, key=order)[0]
    work.language = first_title.lang
    work.title = first_title.title


def set_product_types(work: Work):
    def order(product_type: ProductType):
        hierarchy = ["openalex", "scienti", "minciencias", "scholar"]
        return (
            hierarchy.index(product_type.source)
            if product_type.source in hierarchy
            else float("inf")
        )

    product_types = list(
        map(
            lambda product_type: ProductType(
                name=product_type.type, source=product_type.source
            ),
            work.types,
        )
    )
    work.product_types = sorted(product_types, key=order)


def set_bibliographic_info(work: Work):
    work.issue = work.bibliographic_info.issue
    work.open_access_status = work.bibliographic_info.open_access_status
    work.volume = work.bibliographic_info.volume
    work.bibliographic_info = None


def set_authors_external_ids(work: Work):
    for author in work.authors:
        if author.id:
            author.external_ids = person_repository.get_person_by_id(
                str(author.id)
            ).external_ids


def limit_authors(work: Work, limit: int = 10):
    if len(work.authors) > limit:
        work.authors = work.authors[:limit]


def set_external_ids(work: Work):
    new_external_ids = []
    for external_id in work.external_ids:
        if external_id.source in ["minciencias", "scienti"]:
            new_external_ids.append(external_id)
        else:
            work.external_urls.append(
                ExternalUrl(url=external_id.id, source=external_id.source)
            )
    work.external_ids = list(set(new_external_ids))


def set_external_urls(work: Work):
    new_external_urls = []
    for external_url in work.external_urls:
        url = str(external_url.url)
        if urlparse(url).scheme and urlparse(url).netloc:
            new_external_urls.append(external_url)
        else:
            if external_url.source in external_urls.keys() and url != "":
                new_external_urls.append(
                    ExternalUrl(
                        url=external_urls[external_url.source].format(id=url),
                        source=external_url.source,
                    )
                )
    work.external_urls = list(set(new_external_urls))
