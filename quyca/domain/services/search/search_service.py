import time
from typing import Dict

from quyca.domain.models.base_model import QueryParams
from quyca.domain.parsers.affiliation import affiliation_parser
from quyca.domain.parsers.base_parser import build_metadata
from quyca.domain.parsers.search import search_parser
from quyca.domain.parsers.source import source_parser
from quyca.domain.parsers.work import work_parser
from quyca.domain.services.base_service import get_entity_data
from quyca.infrastructure.repositories.search import (
    search_affiliation_filters_repository,
    search_repository,
    search_source_filters_repository,
    search_work_filters_repository,
)


def search_persons(query_params: QueryParams, current_url: str) -> Dict:
    start_time = time.time()
    persons = search_repository.search_persons(query_params)
    total_count = search_repository.search_count_persons(query_params)
    return build_metadata(
        persons,
        total_count,
        query_params,
        start_time,
        current_url,
        parser=search_parser.parse_persons_search,
    )


def search_works(query_params: QueryParams, current_url: str) -> Dict:
    start_time = time.time()
    works = search_repository.search_works(query_params)
    works_data = get_entity_data(works)
    total_count = search_repository.search_count_works(query_params)
    return build_metadata(
        works_data,
        total_count,
        query_params,
        start_time,
        current_url,
        parser=search_parser.parse_works_search,
    )


def search_affiliations(query_params: QueryParams, affiliation_type: str, current_url) -> Dict:
    start_time = time.time()
    affiliations = search_repository.search_affiliations(affiliation_type, query_params)
    total_count = search_repository.search_count_affiliations(query_params, affiliation_type)
    return build_metadata(
        affiliations,
        total_count,
        query_params,
        start_time,
        current_url,
        parser=search_parser.parse_affiliations_search,
    )


def search_sources(query_params: QueryParams, current_url: str) -> Dict:
    start_time = time.time()
    sources = search_repository.search_sources(query_params)
    total_count = search_repository.search_count_sources(query_params)
    return build_metadata(
        sources,
        total_count,
        query_params,
        start_time,
        current_url,
        parser=search_parser.parse_sources_search,
    )


def search_patents(query_params: QueryParams, current_url: str) -> Dict:
    start_time = time.time()
    patents = search_repository.search_patents(query_params)
    patents_data = get_entity_data(patents)
    total_count = search_repository.search_count_patents(query_params)
    return build_metadata(
        patents_data,
        total_count,
        query_params,
        start_time,
        current_url,
        parser=search_parser.parse_patents_search,
    )


def search_projects(query_params: QueryParams, current_url: str) -> Dict:
    start_time = time.time()
    projects = search_repository.search_projects(query_params)
    projects_data = get_entity_data(projects)
    total_count = search_repository.search_count_projects(query_params)
    return build_metadata(
        projects_data,
        total_count,
        query_params,
        start_time,
        current_url,
        parser=search_parser.parse_projects_search,
    )


def search_geo(query_params: QueryParams, geo_type: str, current_url: str) -> Dict:
    start_time = time.time()
    geolocations = search_repository.search_geo(query_params, geo_type)
    total_count = search_repository.search_count_geo(query_params, geo_type)
    return build_metadata(
        geolocations,
        total_count,
        query_params,
        start_time,
        current_url,
        parser=search_parser.parse_geolocations_search,
    )


def search_works_available_filters(query_params: QueryParams) -> Dict:
    available_filters = search_work_filters_repository.get_works_available_filters(query_params)
    return work_parser.parse_available_filters(available_filters)


def search_affiliations_available_filters(affiliation_type: str, query_params: QueryParams) -> Dict:
    available_filters = search_affiliation_filters_repository.get_affiliations_available_filters(
        affiliation_type, query_params
    )

    return affiliation_parser.parse_available_affiliation_filters(available_filters)


def search_sources_available_filters(query_params: QueryParams) -> dict:
    available_filters = search_source_filters_repository.search_sources_available_filters(query_params)
    return source_parser.parse_available_filters(available_filters)
