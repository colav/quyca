from typing import Any, Dict, Generator, List, Tuple

from pymongo.command_cursor import CommandCursor

from quyca.domain.models.base_model import QueryParams
from quyca.infrastructure.generators import work_generator
from quyca.infrastructure.mongo import database, calculations_database
from quyca.infrastructure.repositories import work_repository
from quyca.infrastructure.repositories import affiliation_repository


def get_affiliations_scienti_works_count_by_institution(
    institution_id: str, relation_type: str, query_params: QueryParams
) -> CommandCursor:
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"relations.id": institution_id, "types.type": relation_type}},
        {"$unwind": "$works"},
        {"$unwind": "$works.types"},
        {"$match": {"works.types.source": "scienti", "works.types.level": 2}},
    ]
    set_plot_product_filters(pipeline, query_params)
    pipeline += [
        {
            "$group": {
                "_id": {"id": "$_id", "type": "$works.types.type", "name": "$names.name"},
                "works_count": {"$sum": "$works.types.count"},
            }
        },
        {"$project": {"_id": 0, "type": "$_id.type", "works_count": 1, "name": {"$first": "$_id.name"}}},
    ]
    return database["affiliations"].aggregate(pipeline)


def get_departments_scienti_works_count_by_faculty(affiliation_id: str, query_params: QueryParams) -> CommandCursor:
    return get_affiliations_scienti_works_count_by_institution(affiliation_id, "department", query_params)


def get_groups_scienti_works_count_by_faculty_or_department(
    affiliation_id: str, query_params: QueryParams
) -> CommandCursor:
    institution_id = (
        database["affiliations"]
        .aggregate(
            [
                {"$match": {"_id": affiliation_id}},
                {"$unwind": "$relations"},
                {"$match": {"relations.types.type": "Education"}},
            ]
        )
        .next()
        .get("relations", {})
        .get("id", None)
    )

    pipeline: List[Dict[str, Any]] = [
        {
            "$match": {
                "relations.id": institution_id,
                "types.type": "group",
            }
        },
        {"$unwind": "$works"},
        {"$unwind": "$works.types"},
        {
            "$match": {
                "works.types.source": "scienti",
                "works.types.level": 2,
            }
        },
    ]
    set_plot_product_filters(pipeline, query_params)
    pipeline += [
        {
            "$group": {
                "_id": {"id": "$_id", "type": "$works.types.type", "name": "$names.name"},
                "works_count": {"$sum": "$works.types.count"},
            }
        },
        {
            "$project": {
                "_id": 0,
                "type": "$_id.type",
                "works_count": 1,
                "name": {"$first": "$_id.name"},
            }
        },
    ]
    return database["affiliations"].aggregate(pipeline)


def get_affiliations_citations_count_by_institution(institution_id: str, relation_type: str) -> CommandCursor:
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"relations.id": institution_id, "types.type": relation_type}},
        {"$project": {"_id": 0, "citations_count": 1, "name": {"$first": "$names.name"}}},
    ]
    return database["affiliations"].aggregate(pipeline)


def get_departments_citations_count_by_faculty(affiliation_id: str) -> CommandCursor:
    return get_affiliations_citations_count_by_institution(affiliation_id, "department")


def get_groups_citations_count_by_faculty_or_department(affiliation_id: str) -> CommandCursor:
    groups_ids = [group.id for group in affiliation_repository.get_groups_by_faculty_or_department(affiliation_id)]
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"groups.id": {"$in": groups_ids}}},
        {"$project": {"groups": 1}},
        {"$unwind": "$groups"},
        {
            "$group": {
                "_id": "$groups.id",
                "name": {"$first": "$groups.name"},
                "citations_count": {"$first": "$groups.citations_count"},
            }
        },
    ]
    return database["works"].aggregate(pipeline)


def get_affiliations_apc_expenses_by_institution(
    institution_id: str, relation_type: str, query_params: QueryParams
) -> CommandCursor:
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"relations.id": institution_id, "types.type": relation_type}},
        {"$unwind": "$works"},
        {"$unwind": "$works.source"},
    ]
    set_plot_product_filters(pipeline, query_params)
    pipeline += [{"$project": {"names": 1, "apc": "$works.source"}}]
    return database["affiliations"].aggregate(pipeline)


def get_departments_apc_expenses_by_faculty(affiliation_id: str, query_params: QueryParams) -> CommandCursor:
    return get_affiliations_apc_expenses_by_institution(affiliation_id, "department", query_params)


def get_groups_apc_expenses_by_faculty_or_department(affiliation_id: str, query_params: QueryParams) -> CommandCursor:
    institution_id = (
        database["affiliations"]
        .aggregate(
            [
                {"$match": {"_id": affiliation_id}},
                {"$unwind": "$relations"},
                {"$match": {"relations.types.type": "Education"}},
            ]
        )
        .next()
        .get("relations", {})
        .get("id", None)
    )
    pipeline: List[Dict[str, Any]] = [
        {
            "$match": {
                "relations.id": institution_id,
                "types.type": "group",
            }
        },
        {"$unwind": "$works"},
        {"$unwind": "$works.source"},
    ]
    set_plot_product_filters(pipeline, query_params)
    pipeline += [{"$project": {"names": 1, "apc": "$works.source"}}]
    return database["affiliations"].aggregate(pipeline)


def get_affiliations_works_citations_count_by_institution(
    institution_id: str, relation_type: str, query_params: QueryParams
) -> CommandCursor:
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"relations.id": institution_id, "types.type": relation_type}},
        {"$unwind": "$works"},
    ]
    set_plot_product_filters(pipeline, query_params)
    pipeline += [
        {
            "$project": {
                "_id": 0,
                "scholar_distribution": "$works.scholar_distribution",
                "name": {"$first": "$names.name"},
            }
        },
    ]
    return database["affiliations"].aggregate(pipeline)


def get_departments_works_citations_count_by_faculty(affiliation_id: str, query_params: QueryParams) -> CommandCursor:
    return get_affiliations_works_citations_count_by_institution(affiliation_id, "department", query_params)


def get_groups_works_citations_count_by_faculty_or_department(
    affiliation_id: str, query_params: QueryParams
) -> CommandCursor:
    institution_id = (
        database["affiliations"]
        .aggregate(
            [
                {"$match": {"_id": affiliation_id}},
                {"$unwind": "$relations"},
                {"$match": {"relations.types.type": "Education"}},
            ]
        )
        .next()
        .get("relations", {})
        .get("id", None)
    )
    pipeline: List[Dict[str, Any]] = [
        {
            "$match": {
                "relations.id": institution_id,
                "types.type": "group",
            }
        },
        {"$unwind": "$works"},
    ]
    set_plot_product_filters(pipeline, query_params)
    pipeline += [
        {
            "$project": {
                "_id": 0,
                "scholar_distribution": "$works.scholar_distribution",
                "name": {"$first": "$names.name"},
            }
        }
    ]
    return database["affiliations"].aggregate(pipeline)


def get_active_authors_by_sex(affiliation_id: str) -> CommandCursor:
    pipeline: List[Dict[str, Any]] = [
        {
            "$match": {
                "affiliations": {"$elemMatch": {"id": affiliation_id, "end_date": -1}},
                "updated.source": "staff",
            }
        },
        {"$project": {"_id": 0, "sex": 1}},
    ]
    return database["person"].aggregate(pipeline)


def get_active_authors_by_age_range(affiliation_id: str) -> CommandCursor:
    pipeline: List[Dict[str, Any]] = [
        {
            "$match": {
                "affiliations": {"$elemMatch": {"id": affiliation_id, "end_date": -1}},
                "updated.source": "staff",
            }
        },
        {"$project": {"_id": 0, "birthdate": 1}},
    ]
    return database["person"].aggregate(pipeline)


def get_products_by_author_age_and_person(person_id: str, query_params: QueryParams) -> CommandCursor:
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"authors.id": person_id}},
    ]
    work_repository.set_product_filters(pipeline, query_params)
    pipeline += [
        {"$project": {"authors": 1, "date_published": 1, "year_published": 1}},
        {
            "$lookup": {
                "from": "person",
                "localField": "authors.id",
                "foreignField": "_id",
                "pipeline": [{"$project": {"birthdate": 1}}],
                "as": "author",
            }
        },
        {"$unwind": "$author"},
        {
            "$project": {
                "work.date_published": "$date_published",
                "work.year_published": "$year_published",
                "birthdate": "$author.birthdate",
            }
        },
    ]
    return database["works"].aggregate(pipeline)


def get_coauthorship_by_country_map_by_affiliation(affiliation_id: str, query_params: QueryParams) -> list:
    data = []
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"authors.affiliations.id": affiliation_id}},
    ]
    work_repository.set_product_filters(pipeline, query_params)
    pipeline += [
        {"$unwind": "$authors"},
        {"$unwind": "$authors.affiliations"},
        {"$group": {"_id": "$authors.affiliations.id", "count": {"$sum": 1}}},
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "_id",
                "foreignField": "_id",
                "as": "affiliation",
                "pipeline": [
                    {
                        "$project": {
                            "addresses.country_code": 1,
                            "addresses.country": 1,
                        }
                    }
                ],
            }
        },
        {"$unwind": "$affiliation"},
        {"$unwind": "$affiliation.addresses"},
    ]
    for work in database["works"].aggregate(pipeline):
        data.append(work)
    return data


def get_coauthorship_by_country_map_by_person(person_id: str, query_params: QueryParams) -> list:
    data = []
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"authors.id": person_id}},
    ]
    work_repository.set_product_filters(pipeline, query_params)
    pipeline += [
        {"$unwind": "$authors"},
        {"$unwind": "$authors.affiliations"},
        {"$group": {"_id": "$authors.affiliations.id", "count": {"$sum": 1}}},
        {"$unwind": "$_id"},
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "_id",
                "foreignField": "_id",
                "as": "affiliation",
                "pipeline": [
                    {
                        "$project": {
                            "addresses.country_code": 1,
                            "addresses.country": 1,
                        }
                    }
                ],
            }
        },
        {
            "$project": {
                "count": 1,
                "affiliation.addresses.country_code": 1,
                "affiliation.addresses.country": 1,
            }
        },
        {"$unwind": "$affiliation"},
        {"$unwind": "$affiliation.addresses"},
    ]
    for work in database["works"].aggregate(pipeline):
        data.append(work)
    return data


def get_coauthorship_by_colombian_department_map_by_affiliation(affiliation_id: str, query_params: QueryParams) -> list:
    data = []
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"authors.affiliations.id": affiliation_id}},
    ]
    work_repository.set_product_filters(pipeline, query_params)
    pipeline += [
        {"$unwind": "$authors"},
        {"$group": {"_id": "$authors.affiliations.id", "count": {"$sum": 1}}},
        {"$unwind": "$_id"},
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "_id",
                "foreignField": "_id",
                "as": "affiliation",
                "pipeline": [
                    {
                        "$project": {
                            "addresses.country_code": 1,
                            "addresses.city": 1,
                        }
                    }
                ],
            }
        },
        {"$unwind": "$affiliation"},
        {"$unwind": "$affiliation.addresses"},
    ]
    for work in database["works"].aggregate(pipeline):
        data.append(work)
    return data


def get_coauthorship_by_colombian_department_map_by_person(person_id: str, query_params: QueryParams) -> list:
    data = []
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"authors.id": person_id}},
    ]
    work_repository.set_product_filters(pipeline, query_params)
    pipeline += [
        {"$unwind": "$authors"},
        {"$group": {"_id": "$authors.affiliations.id", "count": {"$sum": 1}}},
        {"$unwind": "$_id"},
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "_id",
                "foreignField": "_id",
                "as": "affiliation",
            }
        },
        {
            "$project": {
                "count": 1,
                "affiliation.addresses.country_code": 1,
                "affiliation.addresses.city": 1,
            }
        },
        {"$unwind": "$affiliation"},
        {"$unwind": "$affiliation.addresses"},
    ]
    for work in database["works"].aggregate(pipeline):
        data.append(work)
    return data


def get_collaboration_network(affiliation_id: str) -> CommandCursor:
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"_id": affiliation_id}},
        {"$project": {"coauthorship_network": 1}},
        {
            "$lookup": {
                "from": "affiliations_edges",
                "localField": "_id",
                "foreignField": "_id",
                "as": "complement",
            }
        },
        {"$unwind": "$complement"},
        {
            "$project": {
                "coauthorship_network": {
                    "nodes": "$coauthorship_network.nodes",
                    "edges": {
                        "$concatArrays": [
                            "$coauthorship_network.edges",
                            "$complement.coauthorship_network.edges",
                        ]
                    },
                }
            }
        },
    ]
    return calculations_database["affiliations"].aggregate(pipeline)


def get_works_rankings_by_person(person_id: str, query_params: QueryParams) -> Tuple[Generator, int]:
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"authors.id": person_id}},
    ]
    work_repository.set_product_filters(pipeline, query_params)
    pipeline += [
        {
            "$project": {
                "_id": 1,
                "source.id": 1,
                "date_published": 1,
                "source.ranking": 1,
            }
        },
    ]
    count_pipeline: List[Dict[str, Any]] = [
        {"$match": {"authors.id": person_id}},
    ]
    work_repository.set_product_filters(count_pipeline, query_params)

    count_pipeline += [
        {"$count": "total_results"},
    ]

    total_results = next(database["works"].aggregate(count_pipeline), {"total_results": 0})["total_results"]

    works = database["works"].aggregate(pipeline)
    return work_generator.get(works), total_results


def get_products_by_database_by_affiliation(affiliation_id: str) -> dict:
    base_match = {"authors.affiliations.id": affiliation_id}
    valid_sources = ["minciencias", "openalex", "scholar", "scienti"]

    def count_sources(sources: list) -> int:
        return database["works"].count_documents(
            {**base_match, "$expr": {"$setEquals": [{"$setIntersection": ["$updated.source", valid_sources]}, sources]}}
        )

    return {
        "minciencias": count_sources(["minciencias"]),
        "openalex": count_sources(["openalex"]),
        "scholar": count_sources(["scholar"]),
        "scienti": count_sources(["scienti"]),
        "scienti_minciencias": count_sources(["scienti", "minciencias"]),
        "scienti_openalex": count_sources(["scienti", "openalex"]),
        "scienti_scholar": count_sources(["scienti", "scholar"]),
        "minciencias_openalex": count_sources(["minciencias", "openalex"]),
        "minciencias_scholar": count_sources(["minciencias", "scholar"]),
        "openalex_scholar": count_sources(["openalex", "scholar"]),
        "scienti_minciencias_openalex": count_sources(["scienti", "minciencias", "openalex"]),
        "scienti_minciencias_scholar": count_sources(["scienti", "minciencias", "scholar"]),
        "scienti_openalex_scholar": count_sources(["scienti", "openalex", "scholar"]),
        "minciencias_openalex_scholar": count_sources(["minciencias", "openalex", "scholar"]),
        "minciencias_openalex_scholar_scienti": count_sources(["minciencias", "openalex", "scholar", "scienti"]),
    }


def get_products_by_database_by_person(person_id: str) -> dict:
    return {
        "minciencias": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": person_id},
                    {"updated.source": "minciencias"},
                ]
            }
        ),
        "openalex": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": person_id},
                    {"updated.source": "openalex"},
                ]
            }
        ),
        "scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": person_id},
                    {"updated.source": "scholar"},
                ]
            }
        ),
        "scienti": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": person_id},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_minciencias": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": person_id},
                    {"updated.source": "minciencias"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_openalex": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": person_id},
                    {"updated.source": "openalex"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": person_id},
                    {"updated.source": "scholar"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "minciencias_openalex": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": person_id},
                    {"updated.source": "minciencias"},
                    {"updated.source": "openalex"},
                ]
            }
        ),
        "minciencias_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": person_id},
                    {"updated.source": "minciencias"},
                    {"updated.source": "scholar"},
                ]
            }
        ),
        "openalex_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": person_id},
                    {"updated.source": "openalex"},
                    {"updated.source": "scholar"},
                ]
            }
        ),
        "scienti_minciencias_openalex": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": person_id},
                    {"updated.source": "minciencias"},
                    {"updated.source": "openalex"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_minciencias_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": person_id},
                    {"updated.source": "minciencias"},
                    {"updated.source": "scholar"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_openalex_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": person_id},
                    {"updated.source": "openalex"},
                    {"updated.source": "scholar"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "minciencias_openalex_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": person_id},
                    {"updated.source": "minciencias"},
                    {"updated.source": "openalex"},
                    {"updated.source": "scholar"},
                ]
            }
        ),
        "minciencias_openalex_scholar_scienti": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": person_id},
                    {"updated.source": "minciencias"},
                    {"updated.source": "openalex"},
                    {"updated.source": "scholar"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
    }


def set_plot_product_filters(pipeline: list, query_params: QueryParams) -> None:
    set_plot_product_type_filters(pipeline, query_params.product_types)
    set_plot_year_filters(pipeline, query_params.years)
    set_plot_status_filters(pipeline, query_params.status)
    set_plot_subject_filters(pipeline, query_params.subjects)
    set_plot_country_filters(pipeline, query_params.countries)
    set_plot_groups_ranking_filters(pipeline, query_params.groups_ranking)
    set_plot_authors_ranking_filters(pipeline, query_params.authors_ranking)


def set_plot_product_type_filters(pipeline: list, type_filters: str | None) -> None:
    if not type_filters:
        return
    match_filters = []
    for type_filter in type_filters.split(","):
        source, type_name = type_filter.split("_")
        match_filters.append({"works.types.source": source, "works.types.type": type_name})
    pipeline += [{"$match": {"$or": match_filters}}]


def set_plot_year_filters(pipeline: list, years: str | None) -> None:
    if not years:
        return
    year_list = [int(year) for year in years.split(",")]
    first_year = min(year_list)
    last_year = max(year_list)
    pipeline += [{"$match": {"works.year_published": {"$gte": first_year, "$lte": last_year}}}]


def set_plot_status_filters(pipeline: list, status: str | None) -> None:
    if not status:
        return
    match_filters: List[Dict[str, Any]] = []
    for single_status in status.split(","):
        if single_status == "unknown":
            match_filters.append({"works.open_access.open_access_status": None})
        elif single_status == "open":
            match_filters.append({"works.open_access.open_access_status": {"$nin": [None, "closed"]}})
        else:
            match_filters.append({"works.open_access.open_access_status": single_status})
    pipeline += [{"$match": {"$or": match_filters}}]


def set_plot_subject_filters(pipeline: list, subjects: str | None) -> None:
    if not subjects:
        return
    match_filters = []
    for subject in subjects.split(","):
        params = subject.split("_")
        if len(params) == 1:
            return
        match_filters.append({"works.subjects.subjects": {"$elemMatch": {"level": int(params[0]), "name": params[1]}}})
    pipeline += [{"$match": {"$or": match_filters}}]


def set_plot_country_filters(pipeline: list, countries: str | None) -> None:
    if not countries:
        return
    match_filters = []
    for country in countries.split(","):
        match_filters.append({"authors.affiliations": {"$elemMatch": {"country_code": country}}})
    pipeline += [{"$match": {"$or": match_filters}}]


def set_plot_groups_ranking_filters(pipeline: list, groups_ranking: str | None) -> None:
    if not groups_ranking:
        return
    match_filters = []
    for ranking in groups_ranking.split(","):
        match_filters.append({"works.groups": {"$elemMatch": {"ranking": ranking}}})
    pipeline += [{"$match": {"$or": match_filters}}]


def set_plot_authors_ranking_filters(pipeline: list, authors_ranking: str | None) -> None:
    if not authors_ranking:
        return
    match_filters = []
    for ranking in authors_ranking.split(","):
        match_filters.append({"works.authors": {"$elemMatch": {"ranking": ranking}}})
    pipeline += [{"$match": {"$or": match_filters}}]
