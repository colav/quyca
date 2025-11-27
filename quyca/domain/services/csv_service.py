from datetime import datetime
from typing import Any, Generator

from quyca.domain.models.base_model import QueryParams
from quyca.domain.models.work_model import BiblioGraphicInfo, Work
from quyca.infrastructure.repositories import csv_repository
from quyca.domain.constants.institutions import institutions_list
from quyca.domain.constants.openalex_types import openalex_types_dict
from quyca.domain.services import source_service
from quyca.domain.services import work_service
from quyca.domain.parsers import work_parser


def get_works_csv_by_affiliation(affiliation_id: str, query_params: QueryParams) -> str:
    pipeline_params = get_works_project_pipeline_params()
    works = csv_repository.get_works_csv_by_affiliation(affiliation_id, query_params, pipeline_params)
    data = get_csv_data(works)
    return work_parser.parse_csv(data)


def get_works_csv_by_person(person_id: str, query_params: QueryParams) -> str:
    pipeline_params = get_works_project_pipeline_params()
    works = csv_repository.get_works_csv_by_person(person_id, query_params, pipeline_params)
    data = get_csv_data(works)
    return work_parser.parse_csv(data)


def get_works_csv_by_source(source_id: str, query_params: QueryParams) -> str:
    """
    Orchestrate the complete CSV generation process for works from a specific source.

    This is the main service function that coordinates the entire workflow:
    1. Define which fields to retrieve from database (projection)
    2. Query works from database with filters
    3. Process and transform raw data for CSV format
    4. Generate final CSV string

    Args:
        source_id: Unique identifier of the source (institution, journal, etc.)
        query_params: Query parameters for filtering and pagination

    Returns:
        str: Complete CSV file content as string, ready for HTTP response
    """
    pipeline_params = get_works_project_pipeline_params()
    works = csv_repository.get_works_csv_by_source(source_id, query_params, pipeline_params)
    data = get_csv_data(works)
    return work_parser.parse_csv(data)


def get_works_project_pipeline_params() -> dict:
    """
    Define database projection parameters for CSV export.

    Specifies which fields should be retrieved from the database to minimize
    data transfer and improve query performance. Only fields needed for CSV
    export are included.

    Returns:
        dict: Pipeline parameters with 'project' key containing list of field names

    Note:
        Adding new columns to CSV requires adding corresponding fields here
    """
    pipeline_params = {
        "project": [
            "external_ids",
            "authors",
            "bibliographic_info",
            "open_access",
            "citations_count",
            "subjects",
            "titles",
            "types",
            "source",
            "groups",
            "year_published",
            "ranking",
            "primary_topic",
            "doi",
        ]
    }
    return pipeline_params


def get_csv_data(works: Generator) -> list:
    data = []
    for work in works:
        set_open_access_status(work)
        set_doi(work)
        set_csv_ranking(work)
        set_csv_affiliations(work)
        set_csv_authors(work)
        set_csv_bibliographic_info(work)
        set_csv_citations_count(work)
        set_csv_subjects(work)
        work_service.set_title_and_language(work)
        set_csv_types(work)
        set_primary_topic(work)
        source_service.update_csv_work_source(work)
        data.append(work)
    return data


def set_primary_topic(work: Work) -> None:
    if not work.primary_topic:
        work.primary_topic_csv = None
        return

    topic_parts = [
        f"Topic: {work.primary_topic.display_name}" if work.primary_topic.display_name else None,
        f"Subfield: {work.primary_topic.subfield.display_name}" if work.primary_topic.subfield else None,
        f"Field: {work.primary_topic.field.display_name}" if work.primary_topic.field else None,
        f"Domain: {work.primary_topic.domain.display_name}" if work.primary_topic.domain else None,
    ]

    work.primary_topic_csv = " | ".join(filter(None, topic_parts))


def set_open_access_status(work: Work) -> None:
    if work.open_access:
        work.open_access_status = work.open_access.open_access_status


def set_csv_ranking(work: Work) -> None:
    if not work.ranking or not isinstance(work.ranking, list):
        work.ranking = None
        return

    rankings: list = []
    for rank in work.ranking:
        date = None
        if isinstance(rank.date, int):
            date = datetime.fromtimestamp(rank.date).strftime("%d-%m-%Y")
        elif isinstance(rank.date, str):
            date = rank.date

        parts = [str(rank.rank), str(rank.source)]
        if date:
            parts.append(date)
        rankings.append(" / ".join(parts))

    work.ranking = " | ".join(rankings) if rankings else None


def set_doi(work: Work) -> None:
    work.doi = getattr(work, "doi", None) or None


def set_csv_types(work: Work) -> None:
    if not isinstance(work.types, list) or not work.types:
        work.openalex_types = None
        work.scienti_types = None
        work.impactu_types = None
        return

    openalex_types = {
        openalex_types_dict[t.type] if t.type in openalex_types_dict else t.type
        for t in work.types
        if t.source == "openalex" and t.type
    }
    scienti_types = {str(t.type) for t in work.types if t.source == "scienti" and t.type}
    impactu_types = {str(t.type) for t in work.types if t.source == "impactu" and t.type}

    work.openalex_types = " | ".join(sorted(openalex_types)) if openalex_types else None
    work.scienti_types = " | ".join(sorted(scienti_types)) if scienti_types else None
    work.impactu_types = " | ".join(sorted(impactu_types)) if impactu_types else None


def set_csv_subjects(work: Work) -> None:
    if not isinstance(work.subjects, list) or not work.subjects:
        work.subjects = None
        return

    all_subjects = {subject.name for subject in (work.subjects[0].subjects or []) if subject.name}
    work.subjects = " | ".join(sorted(all_subjects)) if all_subjects else None


def set_csv_citations_count(work: Work) -> None:
    if not isinstance(work.citations_count, list):
        work.openalex_citations_count = None
        work.scholar_citations_count = None
        return

    for citation_count in work.citations_count:
        if citation_count.source == "openalex":
            work.openalex_citations_count = str(citation_count.count or 0)
        elif citation_count.source == "scholar":
            work.scholar_citations_count = str(citation_count.count or 0)


def set_csv_bibliographic_info(work: Work) -> None:
    biblio_info: BiblioGraphicInfo | dict[str, Any] = work.bibliographic_info or {}

    raw_bibtex = getattr(biblio_info, "bibtex", None)

    if isinstance(raw_bibtex, str):
        work.bibtex = raw_bibtex.replace("\n", " ")
    else:
        work.bibtex = ""

    work.pages = getattr(biblio_info, "pages", None)
    work.issue = getattr(biblio_info, "issue", "") or ""
    work.start_page = getattr(biblio_info, "start_page", None)
    work.end_page = getattr(biblio_info, "end_page", None)
    work.volume = getattr(biblio_info, "volume", None)


def set_csv_authors(work: Work) -> None:
    authors_full_names = [author.full_name for author in work.authors if author.full_name]
    work.authors_csv = " | ".join(sorted(set(authors_full_names)))


def set_csv_affiliations(work: Work) -> None:
    countries, institutions, departments, faculties, groups = (set(), set(), set(), set(), set())
    groups_ranking = set()

    for author in work.authors or []:
        for affiliation in getattr(author, "affiliations", []) or []:
            affiliation_type = affiliation.types[0].type if affiliation.types else None

            if affiliation_type in institutions_list:
                institutions.add(str(affiliation.name))
                if affiliation.addresses:
                    countries.add(str(affiliation.addresses[0].country))

            elif affiliation_type == "department":
                departments.add(str(affiliation.name))

            elif affiliation_type == "faculty":
                faculties.add(str(affiliation.name))

            elif affiliation_type == "group":
                groups.add(str(affiliation.name))

    if work.groups and isinstance(work.groups, list):
        for group in work.groups:
            if group.ranking:
                for rank in group.ranking:
                    if type(rank.from_date) == int and type(rank.to_date) == int:
                        groups_ranking.add(
                            str(rank.rank)
                            + " / "
                            + datetime.fromtimestamp(rank.from_date).strftime("%d-%m-%Y")
                            + " - "
                            + datetime.fromtimestamp(rank.to_date).strftime("%d-%m-%Y")
                        )
                    elif type(rank.date) == int:
                        groups_ranking.add(
                            str(rank.rank) + " / " + datetime.fromtimestamp(rank.date).strftime("%d-%m-%Y")
                        )

    work.institutions = " | ".join(institutions) or None
    work.departments = " | ".join(departments) or None
    work.faculties = " | ".join(faculties) or None
    work.groups_csv = " | ".join(groups) or None
    work.groups_ranking = " | ".join(groups_ranking) or None
    work.countries = " | ".join(countries) or None
