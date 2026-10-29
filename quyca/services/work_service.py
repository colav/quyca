import time

from quyca.constants.summary_rules import WORK_SUMMARY_FIELDS
from quyca.models.base_model import QueryParams
from quyca.models.work_model import Work, Abstract
from quyca.parsers.base_parser import build_metadata
from quyca.repositories import work_repository
from quyca.services.base_service import (
    build_pipeline_params,
    get_entity_data,
    limit_authors,
    set_authors_affiliation_years,
    set_title_and_language,
    set_product_types,
    set_authors_external_ids,
    set_external_urls,
    set_external_ids,
)
from quyca.parsers import work_parser
from quyca.validators import search_validator


def get_work_by_id(work_id: str, query_params: QueryParams) -> dict:
    work = work_repository.get_work_by_id(work_id)

    set_abstract(work)
    set_external_ids(work)
    set_external_urls(work)
    limit_authors(work)
    set_authors_external_ids(work, filter_sensitive=True)
    set_authors_affiliation_years(work)
    set_title_and_language(work)
    set_product_types(work)
    data = work_parser.parse_work(work)
    return {"data": data}


def get_work_by_doi(work_doi: str, query_params: QueryParams, current_url: str) -> dict:
    start_time = time.time()
    work = work_repository.get_work_by_doi(work_doi)
    return build_metadata(
        work,
        1,
        query_params,
        start_time,
        current_url,
        work_parser.parse_works,
    )


def set_abstract(work: Work) -> None:
    def order(abstract: Abstract) -> float:
        hierarchy = ["openalex", "scholar", "scienti"]
        return hierarchy.index(abstract.source) if abstract.source in hierarchy else float("inf")

    if not work.abstracts:
        return
    first_abstract = sorted(work.abstracts, key=order)[0]
    work.abstract = first_abstract.abstract


def get_work_authors(work_id: str) -> dict:
    work = work_repository.get_work_by_id(work_id)
    set_authors_external_ids(work, filter_sensitive=True)
    return {"data": work.model_dump()["authors"]}


def get_works_by_affiliation(affiliation_id: str, query_params: QueryParams, current_url: str) -> dict:
    search_validator.validate_sort(query_params.sort)
    search_validator.validate_years(query_params.years)
    start_time = time.time()
    pipeline_params = build_pipeline_params(query_params.view, WORK_SUMMARY_FIELDS)
    works = work_repository.get_works_by_affiliation(affiliation_id, query_params, pipeline_params)
    works_data = get_entity_data(works, query_params.view)
    total_results = work_repository.get_works_count_by_affiliation(affiliation_id, query_params)
    return build_metadata(
        works_data,
        total_results,
        query_params,
        start_time,
        current_url,
        work_parser.parse_works,
    )


def get_works_filters_by_affiliation(affiliation_id: str, query_params: QueryParams) -> dict:
    search_validator.validate_years(query_params.years)
    available_filters = work_repository.get_works_available_filters_by_affiliation(affiliation_id, query_params)
    return work_parser.parse_available_filters(available_filters)


def get_works_by_person(person_id: str, query_params: QueryParams, current_url: str) -> dict:
    start_time = time.time()
    pipeline_params = build_pipeline_params(query_params.view, WORK_SUMMARY_FIELDS)
    works = work_repository.get_works_by_person(person_id, query_params, pipeline_params)
    works_data = get_entity_data(works, query_params.view)
    total_results = work_repository.get_works_count_by_person(person_id, query_params)
    return build_metadata(
        works_data,
        total_results,
        query_params,
        start_time,
        current_url,
        parser=work_parser.parse_works,
    )


def get_works_filters_by_person(person_id: str, query_params: QueryParams) -> dict:
    available_filters = work_repository.get_works_available_filters_by_person(person_id, query_params)
    return work_parser.parse_available_filters(available_filters)


def get_works_by_source(source_id: str, query_params: QueryParams, current_url: str) -> dict:
    start_time = time.time()
    pipeline_params = build_pipeline_params(query_params.view, WORK_SUMMARY_FIELDS)
    works = work_repository.get_works_by_source(source_id, query_params, pipeline_params)
    works_data = get_entity_data(works, query_params.view)
    total_results = work_repository.get_works_count_by_source(source_id, query_params)
    return build_metadata(
        works_data,
        total_results,
        query_params,
        start_time,
        current_url,
        parser=work_parser.parse_works,
    )


def get_works_filters_by_source(source_id: str, query_params: QueryParams) -> dict:
    available_filters = work_repository.get_works_available_filters_by_source(source_id, query_params)
    return work_parser.parse_available_filters(available_filters)


def get_works_by_geo(geo_type: str, geo_id: str, query_params: QueryParams, current_url: str) -> dict:
    start_time = time.time()
    pipeline_params = build_pipeline_params(query_params.view, WORK_SUMMARY_FIELDS)
    works = work_repository.get_works_by_geo(geo_type, geo_id, query_params, pipeline_params)

    works_data = get_entity_data(works, query_params.view)
    total_results = work_repository.get_works_count_by_geo(geo_type, geo_id, query_params)
    return build_metadata(
        works_data,
        total_results,
        query_params,
        start_time,
        current_url,
        parser=work_parser.parse_works,
    )
