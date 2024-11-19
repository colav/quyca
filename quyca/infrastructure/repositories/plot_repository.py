from typing import Generator, Tuple

from bson import ObjectId
from pymongo.command_cursor import CommandCursor

from domain.models.base_model import QueryParams
from infrastructure.generators import work_generator
from infrastructure.mongo import database, calculations_database
from infrastructure.repositories import work_repository


def get_affiliations_scienti_works_count_by_institution(
    institution_id: str, relation_type: str, query_params: QueryParams
) -> CommandCursor:
    pipeline = [
        {"$match": {"relations.id": ObjectId(institution_id), "types.type": relation_type}},
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.affiliations.id",
                "as": "works",
                "pipeline": [{"$project": {"types": 1}}],
            }
        },
        {"$unwind": "$works"},
        {"$unwind": "$works.types"},
        {"$match": {"works.types.source": "scienti", "works.types.level": 2}},
    ]
    set_plot_product_filters(pipeline, query_params)
    pipeline += [
        {
            "$group": {
                "_id": {"id": "$_id", "type": "$works.types.type", "name": "$names.name"},
                "works_count": {"$sum": 1},
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
                {"$match": {"_id": ObjectId(affiliation_id)}},
                {"$unwind": "$relations"},
                {"$match": {"relations.types.type": "education"}},
            ]
        )
        .next()
        .get("relations", {})
        .get("id", None)
    )
    pipeline = [
        {
            "$match": {
                "relations.id": institution_id,
                "types.type": "group",
            }
        },
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.affiliations.id",
                "as": "works",
                "pipeline": [{"$project": {"types": 1}}],
            }
        },
        {"$unwind": "$works"},
        {"$unwind": "$works.types"},
        {
            "$match": {
                "works.authors.affiliations.id": ObjectId(affiliation_id),
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
                "works_count": {"$sum": 1},
            }
        },
        {"$project": {"_id": 0, "type": "$_id.type", "works_count": 1, "name": {"$first": "$_id.name"}}},
    ]
    return database["affiliations"].aggregate(pipeline)


def get_affiliations_citations_count_by_institution(institution_id: str, relation_type: str) -> CommandCursor:
    pipeline = [
        {"$match": {"relations.id": ObjectId(institution_id), "types.type": relation_type}},
        {"$project": {"_id": 0, "citations_count": 1, "name": {"$first": "$names.name"}}},
    ]
    return database["affiliations"].aggregate(pipeline)


def get_departments_citations_count_by_faculty(affiliation_id: str) -> CommandCursor:
    return get_affiliations_citations_count_by_institution(affiliation_id, "department")


def get_groups_citations_count_by_faculty_or_department(affiliation_id: str) -> CommandCursor:
    institution_id = (
        database["affiliations"]
        .aggregate(
            [
                {"$match": {"_id": ObjectId(affiliation_id)}},
                {"$unwind": "$relations"},
                {"$match": {"relations.types.type": "education"}},
            ]
        )
        .next()
        .get("relations", {})
        .get("id", None)
    )
    pipeline = [
        {
            "$match": {
                "authors.affiliations.id": ObjectId(affiliation_id),
            }
        },
        {"$unwind": "$groups"},
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "groups.id",
                "foreignField": "_id",
                "as": "group",
                "pipeline": [
                    {
                        "$match": {
                            "relations.id": ObjectId(institution_id),
                            "types.type": "group",
                        },
                    },
                    {"$project": {"_id": 1, "name": {"$first": "$names.name"}, "citations_count": 1}},
                ],
            }
        },
        {"$unwind": "$group"},
        {"$replaceRoot": {"newRoot": "$group"}},
        {
            "$group": {
                "_id": "$_id",
                "name": {"$first": "$name"},
                "citations_count": {"$first": "$citations_count"},
            }
        },
    ]
    return database["works"].aggregate(pipeline)


def get_affiliations_apc_expenses_by_institution(
    institution_id: str, relation_type: str, query_params: QueryParams
) -> CommandCursor:
    pipeline = [
        {"$match": {"relations.id": ObjectId(institution_id), "types.type": relation_type}},
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.affiliations.id",
                "as": "works",
                "pipeline": [{"$project": {"source": 1}}],
            }
        },
        {"$unwind": "$works"},
    ]
    set_plot_product_filters(pipeline, query_params)
    pipeline += [
        {
            "$lookup": {
                "from": "sources",
                "localField": "works.source.id",
                "foreignField": "_id",
                "as": "source",
                "pipeline": [{"$project": {"apc": 1}}],
            }
        },
        {"$unwind": "$source"},
        {"$project": {"_id": 0, "source": 1, "names": 1}},
    ]
    return database["affiliations"].aggregate(pipeline)


def get_departments_apc_expenses_by_faculty(affiliation_id: str, query_params: QueryParams) -> CommandCursor:
    return get_affiliations_apc_expenses_by_institution(affiliation_id, "department", query_params)


def get_groups_apc_expenses_by_faculty_or_department(affiliation_id: str, query_params: QueryParams) -> CommandCursor:
    institution_id = (
        database["affiliations"]
        .aggregate(
            [
                {"$match": {"_id": ObjectId(affiliation_id)}},
                {"$unwind": "$relations"},
                {"$match": {"relations.types.type": "education"}},
            ]
        )
        .next()
        .get("relations", {})
        .get("id", None)
    )
    pipeline = [
        {
            "$match": {
                "relations.id": institution_id,
                "types.type": "group",
            }
        },
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.affiliations.id",
                "as": "works",
                "pipeline": [
                    {"$match": {"authors.affiliations.id": ObjectId(affiliation_id)}},
                    {"$project": {"source": 1, "authors": 1}},
                ],
            }
        },
        {"$unwind": "$works"},
    ]
    set_plot_product_filters(pipeline, query_params)
    pipeline += [
        {
            "$lookup": {
                "from": "sources",
                "localField": "works.source.id",
                "foreignField": "_id",
                "as": "source",
                "pipeline": [{"$project": {"apc": 1}}],
            }
        },
        {"$unwind": "$source"},
        {"$project": {"_id": 0, "source": 1, "names": 1}},
    ]
    return database["affiliations"].aggregate(pipeline)


def get_affiliations_works_citations_count_by_institution(
    institution_id: str, relation_type: str, query_params: QueryParams
) -> CommandCursor:
    pipeline = [
        {"$match": {"relations.id": ObjectId(institution_id), "types.type": relation_type}},
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.affiliations.id",
                "as": "works",
                "pipeline": [
                    {
                        "$addFields": {
                            "scholar_citations_count": {
                                "$ifNull": [
                                    {
                                        "$arrayElemAt": [
                                            {
                                                "$map": {
                                                    "input": {
                                                        "$filter": {
                                                            "input": "$citations_count",
                                                            "as": "citation",
                                                            "cond": {
                                                                "$eq": [
                                                                    "$$citation.source",
                                                                    "scholar",
                                                                ]
                                                            },
                                                        }
                                                    },
                                                    "as": "filtered",
                                                    "in": "$$filtered.count",
                                                }
                                            },
                                            0,
                                        ]
                                    },
                                    0,
                                ]
                            }
                        }
                    },
                    {"$project": {"scholar_citations_count": 1}},
                ],
            }
        },
    ]
    set_plot_product_filters(pipeline, query_params)
    pipeline += [
        {"$project": {"_id": 0, "works": 1, "name": {"$first": "$names.name"}}},
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
                {"$match": {"_id": ObjectId(affiliation_id)}},
                {"$unwind": "$relations"},
                {"$match": {"relations.types.type": "education"}},
            ]
        )
        .next()
        .get("relations", {})
        .get("id", None)
    )
    pipeline = [
        {
            "$match": {
                "relations.id": institution_id,
                "types.type": "group",
            }
        },
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.affiliations.id",
                "as": "works",
                "pipeline": [
                    {"$match": {"authors.affiliations.id": ObjectId(affiliation_id)}},
                    {
                        "$addFields": {
                            "scholar_citations_count": {
                                "$ifNull": [
                                    {
                                        "$arrayElemAt": [
                                            {
                                                "$map": {
                                                    "input": {
                                                        "$filter": {
                                                            "input": "$citations_count",
                                                            "as": "citation",
                                                            "cond": {
                                                                "$eq": [
                                                                    "$$citation.source",
                                                                    "scholar",
                                                                ]
                                                            },
                                                        }
                                                    },
                                                    "as": "filtered",
                                                    "in": "$$filtered.count",
                                                }
                                            },
                                            0,
                                        ]
                                    },
                                    0,
                                ]
                            }
                        }
                    },
                    {"$project": {"scholar_citations_count": 1}},
                ],
            }
        },
    ]
    set_plot_product_filters(pipeline, query_params)
    pipeline += [
        {"$project": {"_id": 0, "works": 1, "name": {"$first": "$names.name"}}},
    ]
    return database["affiliations"].aggregate(pipeline)


def get_active_authors_by_sex(affiliation_id: str) -> CommandCursor:
    pipeline = [
        {
            "$match": {
                "affiliations": {"$elemMatch": {"id": ObjectId(affiliation_id), "end_date": -1}},
                "ranking.source": "staff",
            }
        },
        {"$project": {"_id": 0, "sex": 1}},
    ]
    return database["person"].aggregate(pipeline)


def get_active_authors_by_age_range(affiliation_id: str) -> CommandCursor:
    pipeline = [
        {
            "$match": {
                "affiliations": {"$elemMatch": {"id": ObjectId(affiliation_id), "end_date": -1}},
                "ranking.source": "staff",
            }
        },
        {"$project": {"_id": 0, "birthdate": 1}},
    ]
    return database["person"].aggregate(pipeline)


def get_products_by_author_age_and_person(person_id: str, query_params: QueryParams) -> CommandCursor:
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
    ]
    work_repository.set_product_filters(pipeline, query_params)
    pipeline += [
        {"$project": {"authors": 1, "date_published": 1, "year_published": 1}},  # type: ignore
        {
            "$lookup": {
                "from": "person",  # type: ignore
                "localField": "authors.id",  # type: ignore
                "foreignField": "_id",  # type: ignore
                "pipeline": [{"$project": {"birthdate": 1}}],  # type: ignore
                "as": "author",  # type: ignore
            }
        },
        {"$unwind": "$author"},  # type: ignore
        {
            "$project": {
                "work.date_published": "$date_published",  # type: ignore
                "work.year_published": "$year_published",  # type: ignore
                "birthdate": "$author.birthdate",  # type: ignore
            }
        },
    ]
    return database["works"].aggregate(pipeline)


def get_coauthorship_by_country_map_by_affiliation(affiliation_id: str, query_params: QueryParams) -> list:
    data = []
    pipeline = [
        {"$match": {"authors.affiliations.id": ObjectId(affiliation_id)}},
    ]
    work_repository.set_product_filters(pipeline, query_params)
    pipeline += [
        {"$unwind": "$authors"},  # type: ignore
        {"$unwind": "$authors.affiliations"},  # type: ignore
        {"$group": {"_id": "$authors.affiliations.id", "count": {"$sum": 1}}},  # type: ignore
        {
            "$lookup": {
                "from": "affiliations",  # type: ignore
                "localField": "_id",  # type: ignore
                "foreignField": "_id",  # type: ignore
                "as": "affiliation",  # type: ignore
                "pipeline": [  # type: ignore
                    {
                        "$project": {
                            "addresses.country_code": 1,
                            "addresses.country": 1,
                        }
                    }
                ],
            }
        },
        {"$unwind": "$affiliation"},  # type: ignore
        {"$unwind": "$affiliation.addresses"},  # type: ignore
    ]
    for work in database["works"].aggregate(pipeline):
        data.append(work)
    return data


def get_coauthorship_by_country_map_by_person(person_id: str, query_params: QueryParams) -> list:
    data = []
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
    ]
    work_repository.set_product_filters(pipeline, query_params)
    pipeline += [
        {"$unwind": "$authors"},  # type: ignore
        {"$unwind": "$authors.affiliations"},  # type: ignore
        {"$group": {"_id": "$authors.affiliations.id", "count": {"$sum": 1}}},  # type: ignore
        {"$unwind": "$_id"},  # type: ignore
        {
            "$lookup": {
                "from": "affiliations",  # type: ignore
                "localField": "_id",  # type: ignore
                "foreignField": "_id",  # type: ignore
                "as": "affiliation",  # type: ignore
                "pipeline": [  # type: ignore
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
                "count": 1,  # type: ignore
                "affiliation.addresses.country_code": 1,  # type: ignore
                "affiliation.addresses.country": 1,  # type: ignore
            }
        },
        {"$unwind": "$affiliation"},  # type: ignore
        {"$unwind": "$affiliation.addresses"},  # type: ignore
    ]
    for work in database["works"].aggregate(pipeline):
        data.append(work)
    return data


def get_coauthorship_by_colombian_department_map_by_affiliation(affiliation_id: str, query_params: QueryParams) -> list:
    data = []
    pipeline = [
        {"$match": {"authors.affiliations.id": ObjectId(affiliation_id)}},
    ]
    work_repository.set_product_filters(pipeline, query_params)
    pipeline += [
        {"$unwind": "$authors"},  # type: ignore
        {"$group": {"_id": "$authors.affiliations.id", "count": {"$sum": 1}}},  # type: ignore
        {"$unwind": "$_id"},  # type: ignore
        {
            "$lookup": {
                "from": "affiliations",  # type: ignore
                "localField": "_id",  # type: ignore
                "foreignField": "_id",  # type: ignore
                "as": "affiliation",  # type: ignore
                "pipeline": [  # type: ignore
                    {
                        "$project": {
                            "addresses.country_code": 1,
                            "addresses.city": 1,
                        }
                    }
                ],
            }
        },
        {"$unwind": "$affiliation"},  # type: ignore
        {"$unwind": "$affiliation.addresses"},  # type: ignore
    ]
    for work in database["works"].aggregate(pipeline):
        data.append(work)
    return data


def get_coauthorship_by_colombian_department_map_by_person(person_id: str, query_params: QueryParams) -> list:
    data = []
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
    ]
    work_repository.set_product_filters(pipeline, query_params)
    pipeline += [
        {"$unwind": "$authors"},  # type: ignore
        {"$group": {"_id": "$authors.affiliations.id", "count": {"$sum": 1}}},  # type: ignore
        {"$unwind": "$_id"},  # type: ignore
        {
            "$lookup": {
                "from": "affiliations",  # type: ignore
                "localField": "_id",  # type: ignore
                "foreignField": "_id",  # type: ignore
                "as": "affiliation",  # type: ignore
            }
        },
        {
            "$project": {
                "count": 1,  # type: ignore
                "affiliation.addresses.country_code": 1,  # type: ignore
                "affiliation.addresses.city": 1,  # type: ignore
            }
        },
        {"$unwind": "$affiliation"},  # type: ignore
        {"$unwind": "$affiliation.addresses"},  # type: ignore
    ]
    for work in database["works"].aggregate(pipeline):
        data.append(work)
    return data


def get_collaboration_network(affiliation_id: str) -> CommandCursor:
    pipeline = [
        {"$match": {"_id": ObjectId(affiliation_id)}},
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
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
    ]
    work_repository.set_product_filters(pipeline, query_params)
    pipeline += [
        {
            "$lookup": {
                "from": "sources",  # type: ignore
                "localField": "source.id",  # type: ignore
                "foreignField": "_id",  # type: ignore
                "as": "source_data",  # type: ignore
                "pipeline": [  # type: ignore
                    {"$project": {"_id": 1, "ranking": 1}},
                ],
            }
        },
        {"$unwind": "$source_data"},  # type: ignore
        {"$project": {"_id": 1, "source_data": 1, "date_published": 1}},  # type: ignore
    ]
    count_pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
    ]
    work_repository.set_product_filters(count_pipeline, query_params)
    count_pipeline += [
        {"$count": "total_results"},  # type: ignore
    ]
    total_results = next(database["works"].aggregate(count_pipeline), {"total_results": 0})["total_results"]
    works = database["works"].aggregate(pipeline)
    return work_generator.get(works), total_results


def get_products_by_database_by_affiliation(affiliation_id: str) -> dict:
    return {
        "minciencias": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                ]
            }
        ),
        "openalex": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "openalex"},
                ]
            }
        ),
        "scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "scholar"},
                ]
            }
        ),
        "scienti": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_minciencias": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_openalex": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "openalex"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "scholar"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "minciencias_openalex": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "openalex"},
                ]
            }
        ),
        "minciencias_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "scholar"},
                ]
            }
        ),
        "openalex_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "openalex"},
                    {"updated.source": "scholar"},
                ]
            }
        ),
        "scienti_minciencias_openalex": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "openalex"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_minciencias_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "scholar"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_openalex_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "openalex"},
                    {"updated.source": "scholar"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "minciencias_openalex_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "openalex"},
                    {"updated.source": "scholar"},
                ]
            }
        ),
        "minciencias_openalex_scholar_scienti": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "openalex"},
                    {"updated.source": "scholar"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
    }


def get_products_by_database_by_person(affiliation_id: str) -> dict:
    return {
        "minciencias": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                ]
            }
        ),
        "openalex": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "openalex"},
                ]
            }
        ),
        "scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "scholar"},
                ]
            }
        ),
        "scienti": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_minciencias": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_openalex": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "openalex"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "scholar"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "minciencias_openalex": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "openalex"},
                ]
            }
        ),
        "minciencias_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "scholar"},
                ]
            }
        ),
        "openalex_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "openalex"},
                    {"updated.source": "scholar"},
                ]
            }
        ),
        "scienti_minciencias_openalex": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "openalex"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_minciencias_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "scholar"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_openalex_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "openalex"},
                    {"updated.source": "scholar"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "minciencias_openalex_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "openalex"},
                    {"updated.source": "scholar"},
                ]
            }
        ),
        "minciencias_openalex_scholar_scienti": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "openalex"},
                    {"updated.source": "scholar"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
    }


def set_plot_product_filters(pipeline: list, query_params: QueryParams) -> None:
    set_plot_product_type_filters(pipeline, query_params.product_type)
    set_plot_year_filters(pipeline, query_params.year)
    set_plot_status_filters(pipeline, query_params.status)
    set_plot_subject_filters(pipeline, query_params.subject)
    set_plot_country_filters(pipeline, query_params.country)
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
    match_filters = []
    for single_status in status.split(","):
        if single_status == "unknown":
            match_filters.append({"works.open_access.open_access_status": None})
        elif single_status == "open":
            match_filters.append({"works.open_access.open_access_status": {"$nin": [None, "closed"]}})  # type: ignore
        else:
            match_filters.append({"works.open_access.open_access_status": single_status})  # type: ignore
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
        match_filters.append({"works.authors.affiliations": {"$elemMatch": {"country_code": country}}})
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
