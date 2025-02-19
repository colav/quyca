from typing import Generator, Tuple

from bson import ObjectId

from infrastructure.generators import work_generator
from domain.models.base_model import QueryParams
from domain.models.work_model import Work
from infrastructure.repositories import base_repository
from infrastructure.mongo import database
from domain.exceptions.not_entity_exception import NotEntityException


def get_work_by_id(work_id: str) -> Work:
    work = database["works"].find_one(ObjectId(work_id))
    if not work:
        raise NotEntityException(f"The work with id {work_id} does not exist.")
    return Work(**work)


def get_works_by_affiliation(
    affiliation_id: str,
    query_params: QueryParams,
    pipeline_params: dict | None = None,
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {
            "$match": {
                "authors.affiliations.id": affiliation_id,
            },
        },
    ]
    set_product_filters(pipeline, query_params)
    base_repository.set_match(pipeline, pipeline_params.get("match"))
    if sort := query_params.sort:
        base_repository.set_sort(sort, pipeline)
    base_repository.set_pagination(pipeline, query_params)
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_with_source_by_affiliation(
    affiliation_id: str, query_params: QueryParams, pipeline_params: dict | None = None
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    source_project = pipeline_params.get("source_project", [])
    pipeline = [
        {"$match": {"authors.affiliations.id": affiliation_id}},
    ]
    set_product_filters(pipeline, query_params)
    pipeline += [
        {
            "$lookup": {
                "from": "sources",  # type: ignore
                "localField": "source.id",  # type: ignore
                "foreignField": "_id",  # type: ignore
                "as": "source",  # type: ignore
                "pipeline": [{"$project": {"_id": 1, **{p: 1 for p in source_project}}}],  # type: ignore
            }
        },
        {"$unwind": "$source"},  # type: ignore
    ]
    base_repository.set_match(pipeline, pipeline_params.get("match"))
    base_repository.set_project(pipeline, pipeline_params.get("work_project"))
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_count_by_affiliation(affiliation_id: str, query_params: QueryParams) -> int:
    pipeline = [
        {
            "$match": {
                "authors.affiliations.id": affiliation_id,
            },
        },
    ]
    set_product_filters(pipeline, query_params)
    pipeline += [{"$count": "total"}]  # type: ignore
    return next(database["works"].aggregate(pipeline), {"total": 0}).get("total", 0)


def get_works_by_person(person_id: str, query_params: QueryParams, pipeline_params: dict | None = None) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
    ]
    set_product_filters(pipeline, query_params)
    base_repository.set_match(pipeline, pipeline_params.get("match"))
    if sort := query_params.sort:
        base_repository.set_sort(sort, pipeline)
    base_repository.set_pagination(pipeline, query_params)
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_with_source_by_person(
    person_id: str, query_params: QueryParams, pipeline_params: dict | None = None
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    source_project = pipeline_params.get("source_project", [])
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
    ]
    set_product_filters(pipeline, query_params)
    pipeline += [
        {
            "$lookup": {
                "from": "sources",  # type: ignore
                "localField": "source.id",  # type: ignore
                "foreignField": "_id",  # type: ignore
                "as": "source",  # type: ignore
                "pipeline": [{"$project": {"_id": 1, **{p: 1 for p in source_project}}}],  # type: ignore
            }
        },
        {"$unwind": "$source"},  # type: ignore
    ]
    base_repository.set_match(pipeline, pipeline_params.get("match"))
    base_repository.set_project(pipeline, pipeline_params.get("work_project"))
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_count_by_person(person_id: str, query_params: QueryParams) -> int:
    pipeline = [{"$match": {"authors.id": ObjectId(person_id)}}]
    set_product_filters(pipeline, query_params)
    pipeline += [{"$count": "total"}]  # type: ignore
    return next(database["works"].aggregate(pipeline), {"total": 0}).get("total", 0)


def search_works(query_params: QueryParams, pipeline_params: dict | None = None) -> Tuple[Generator, int]:
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    set_product_filters(pipeline, query_params)
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    works = database["works"].aggregate(pipeline)
    count_pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    set_product_filters(count_pipeline, query_params)
    count_pipeline += [
        {"$count": "total_results"},  # type: ignore
    ]
    total_results = next(database["works"].aggregate(count_pipeline), {"total_results": 0}).get("total_results", 0)
    return work_generator.get(works), total_results


def get_works_available_filters_by_person(person_id: str, query_params: QueryParams) -> dict:
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
    ]
    return get_works_available_filters(pipeline, query_params)


def get_works_available_filters_by_affiliation(affiliation_id: str, query_params: QueryParams) -> dict:
    pipeline = [
        {"$match": {"authors.affiliations.id": affiliation_id}},
    ]
    return get_works_available_filters(pipeline, query_params)


def get_search_works_available_filters(query_params: QueryParams, pipeline_params: dict | None = None) -> dict:
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    return get_works_available_filters(pipeline, query_params)


def get_works_available_filters(pipeline: list, query_params: QueryParams) -> dict:
    set_product_filters(pipeline, query_params)
    available_filters: dict = {}
    product_types_pipeline = pipeline.copy() + [
        {"$unwind": "$types"},
        {"$project": {"types.provenance": 0}},
        {"$group": {"_id": "$types.source", "types": {"$addToSet": "$types"}}},
    ]
    product_types = database["works"].aggregate(product_types_pipeline)
    available_filters["product_types"] = list(product_types)
    years_pipeline = pipeline.copy() + [
        {"$match": {"year_published": {"$type": "number"}}},
        {"$group": {"_id": None, "min_year": {"$min": "$year_published"}, "max_year": {"$max": "$year_published"}}},
        {"$project": {"_id": 0, "min_year": 1, "max_year": 1}},
    ]
    years = database["works"].aggregate(years_pipeline)
    available_filters["years"] = next(years, {"min_year": None, "max_year": None})
    status_pipeline = pipeline.copy() + [
        {"$group": {"_id": "$open_access.open_access_status"}},
    ]
    status = database["works"].aggregate(status_pipeline)
    available_filters["status"] = list(status)
    subjects_pipeline = pipeline.copy() + [
        {"$unwind": "$subjects"},
        {"$unwind": "$subjects.subjects"},
        {"$match": {"subjects.subjects.level": {"$in": [0, 1]}}},
        {"$group": {"_id": "$subjects.source", "subjects": {"$addToSet": "$subjects.subjects"}}},
    ]
    subjects = database["works"].aggregate(subjects_pipeline)
    available_filters["subjects"] = list(next(subjects, {"subjects": []}).get("subjects"))  # type: ignore
    countries_pipeline = pipeline.copy() + [
        {"$unwind": "$authors"},
        {"$unwind": "$authors.affiliations"},
        {
            "$group": {
                "_id": "$authors.affiliations.country_code",
            }
        },
    ]
    countries = database["works"].aggregate(countries_pipeline)
    available_filters["countries"] = list(countries)
    groups_ranking_pipeline = pipeline.copy() + [
        {"$unwind": "$groups"},
        {"$group": {"_id": "$groups.ranking"}},
    ]
    groups_ranking = database["works"].aggregate(groups_ranking_pipeline)
    available_filters["groups_ranking"] = list(groups_ranking)
    authors_ranking_pipeline = pipeline.copy() + [
        {"$unwind": "$authors"},
        {"$group": {"_id": "$authors.ranking"}},
    ]
    authors_ranking = database["works"].aggregate(authors_ranking_pipeline)
    available_filters["authors_ranking"] = list(authors_ranking)
    return available_filters


def set_product_filters(pipeline: list, query_params: QueryParams) -> None:
    set_product_type_filters(pipeline, query_params.product_types)
    set_year_filters(pipeline, query_params.years)
    set_status_filters(pipeline, query_params.status)
    set_subject_filters(pipeline, query_params.subjects)
    set_country_filters(pipeline, query_params.countries)
    set_groups_ranking_filters(pipeline, query_params.groups_ranking)
    set_authors_ranking_filters(pipeline, query_params.authors_ranking)


def set_product_type_filters(pipeline: list, type_filters: str | None) -> None:
    if not type_filters:
        return
    match_filters = []
    for type_filter in type_filters.split(","):
        params = type_filter.split("_")
        if len(params) == 1:
            match_filters.append({"types": {"$elemMatch": {"source": params[0]}}})
        elif len(params) == 2:
            match_filters.append({"types": {"$elemMatch": {"source": params[0], "type": params[1]}}})
        elif len(params) == 3 and params[0] == "scienti":
            match_filters.append(
                {"types": {"$elemMatch": {"source": params[0], "type": params[1], "code": {"$regex": "^" + params[2]}}}}  # type: ignore
            )
    pipeline += [{"$match": {"$or": match_filters}}]


def set_year_filters(pipeline: list, years: str | None) -> None:
    if not years:
        return
    year_list = [int(year) for year in years.split(",")]
    first_year = min(year_list)
    last_year = max(year_list)
    pipeline += [{"$match": {"year_published": {"$gte": first_year, "$lte": last_year}}}]


def set_status_filters(pipeline: list, status: str | None) -> None:
    if not status:
        return
    match_filters = []
    for single_status in status.split(","):
        if single_status == "unknown":
            match_filters.append({"open_access.open_access_status": None})
        elif single_status == "open":
            match_filters.append({"open_access.open_access_status": {"$nin": [None, "closed"]}})  # type: ignore
        else:
            match_filters.append({"open_access.open_access_status": single_status})  # type: ignore
    pipeline += [{"$match": {"$or": match_filters}}]


def set_subject_filters(pipeline: list, subjects: str | None) -> None:
    if not subjects:
        return
    match_filters = []
    for subject in subjects.split(","):
        params = subject.split("_")
        if len(params) == 1:
            return
        match_filters.append({"subjects.subjects": {"$elemMatch": {"level": int(params[0]), "name": params[1]}}})
    pipeline += [{"$match": {"$or": match_filters}}]


def set_country_filters(pipeline: list, countries: str | None) -> None:
    if not countries:
        return
    match_filters = []
    for country in countries.split(","):
        match_filters.append({"authors.affiliations": {"$elemMatch": {"country_code": country}}})
    pipeline += [{"$match": {"$or": match_filters}}]


def set_groups_ranking_filters(pipeline: list, groups_ranking: str | None) -> None:
    if not groups_ranking:
        return
    match_filters = []
    for ranking in groups_ranking.split(","):
        match_filters.append({"groups": {"$elemMatch": {"ranking": ranking}}})
    pipeline += [{"$match": {"$or": match_filters}}]


def set_authors_ranking_filters(pipeline: list, authors_ranking: str | None) -> None:
    if not authors_ranking:
        return
    match_filters = []
    for ranking in authors_ranking.split(","):
        match_filters.append({"authors": {"$elemMatch": {"ranking": ranking}}})
    pipeline += [{"$match": {"$or": match_filters}}]
