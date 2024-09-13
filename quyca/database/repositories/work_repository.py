from typing import Optional, Generator

from bson import ObjectId

from core.config import settings
from database.generators import source_generator
from database.generators import work_generator
from database.models.base_model import QueryParams
from database.models.work_model import Work
from database.repositories import base_repository
from database.mongo import database
from exceptions.work_exception import WorkException


def get_work_by_id(work_id: id) -> Work:
    work = database["works"].find_one(ObjectId(work_id))
    if not work:
        raise WorkException(work_id)
    return Work(**work)


def get_works_by_affiliation(
    affiliation_id: str,
    affiliation_type: str,
    query_params: QueryParams,
    pipeline_params: dict | None = None,
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = get_works_by_affiliation_pipeline(affiliation_id, affiliation_type)
    collection = "affiliations" if affiliation_type in ["faculty", "department"] else "works"
    if collection == "affiliations":
        pipeline += [{"$replaceRoot": {"newRoot": "$works"}}]
    base_repository.set_pagination(pipeline, query_params)
    cursor = database[collection].aggregate(pipeline)
    return work_generator.get(cursor)


def search_works(
    query_params: QueryParams, pipeline_params: dict | None = None
) -> (Generator, int):
    pipeline = (
        [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    )
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    works = database["works"].aggregate(pipeline)
    count_pipeline = (
        [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    )
    count_pipeline += [
        {"$count": "total_results"},
    ]
    total_results = next(database["works"].aggregate(count_pipeline), {"total_results": 0})[
        "total_results"
    ]
    return work_generator.get(works), total_results


def get_sources_by_affiliation(
    affiliation_id: str, affiliation_type: str, pipeline_params: dict | None = None
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    collection = "affiliations" if affiliation_type in ["faculty", "department"] else "works"
    pipeline = get_sources_by_affiliation_pipeline(affiliation_id, affiliation_type)
    if match_param := pipeline_params.get("match"):
        pipeline += [{"$match": match_param}]
    project = pipeline_params["project"]
    if "ranking" in project:
        pipeline += [
            {
                "$addFields": {
                    "ranking": {
                        "$filter": {
                            "input": "$ranking",
                            "as": "rank",
                            "cond": {
                                "$and": [
                                    {"$lte": ["$$rank.from_date", "$date_published"]},
                                    {"$gte": ["$$rank.to_date", "$date_published"]},
                                ]
                            },
                        }
                    }
                }
            },
        ]
    pipeline += [{"$project": {"_id": 1, **{p: 1 for p in project}}}]
    cursor = database[collection].aggregate(pipeline)
    return source_generator.get(cursor)


def get_works_count_by_affiliation(
    affiliation_id: str, affiliation_type: str, filters: dict | None = None
) -> int:
    affiliation_type = (
        "institution" if affiliation_type in settings.institutions else affiliation_type
    )
    pipeline = get_works_by_affiliation_pipeline(affiliation_id, affiliation_type)
    collection = "affiliations" if affiliation_type in ["department", "faculty"] else "works"
    if collection == "affiliations":
        pipeline += [{"$replaceRoot": {"newRoot": "$works"}}]
    pipeline += [{"$count": "total"}]
    works_count = next(database[collection].aggregate(pipeline), {"total": 0}).get("total", 0)
    return works_count


def get_sources_by_related_affiliation(
    affiliation_id: str,
    affiliation_type: str,
    relation_type: str,
    pipeline_params: dict | None = None,
) -> Generator:
    from database.repositories import affiliation_repository

    if pipeline_params is None:
        pipeline_params = {}
    pipeline = affiliation_repository.get_related_affiliations_by_type_pipeline(
        affiliation_id, affiliation_type, relation_type
    )
    pipeline += [{"$project": {"id": 1, "names": 1}}]
    if relation_type == "group":
        pipeline += [
            {
                "$lookup": {
                    "from": "works",
                    "localField": "_id",
                    "foreignField": "groups.id",
                    "as": "works",
                }
            }
        ]
    else:
        pipeline += [
            {
                "$lookup": {
                    "from": "person",
                    "localField": "_id",
                    "foreignField": "affiliations.id",
                    "as": "authors",
                },
            },
            {"$unwind": "$authors"},
            {
                "$project": {
                    "authors_id": "$authors._id",
                    "id": 1,
                    "names": 1,
                },
            },
            {
                "$lookup": {
                    "from": "works",
                    "localField": "authors_id",
                    "foreignField": "authors.id",
                    "as": "works",
                },
            },
        ]
    pipeline += [
        {"$unwind": "$works"},
        {
            "$lookup": {
                "from": "sources",
                "localField": "works.source.id",
                "foreignField": "_id",
                "as": "source",
            }
        },
        {"$unwind": "$source"},
        {
            "$addFields": {
                "source.apc.year_published": "$works.year_published",
                "source.date_published": "$works.date_published",
                "source.affiliation_names": "$names",
            }
        },
        {"$replaceRoot": {"newRoot": "$source"}},
    ]
    project = pipeline_params.get("project")
    if project:
        if "ranking" in pipeline_params["project"]:
            pipeline += [
                {
                    "$addFields": {
                        "ranking": {
                            "$filter": {
                                "input": "$ranking",
                                "as": "rank",
                                "cond": {
                                    "$and": [
                                        {
                                            "$lte": [
                                                "$$rank.from_date",
                                                "$date_published",
                                            ]
                                        },
                                        {"$gte": ["$$rank.to_date", "$date_published"]},
                                    ]
                                },
                            }
                        }
                    }
                },
            ]
        pipeline += [{"$project": {"_id": 1, **{p: 1 for p in project}}}]
    sources = database["affiliations"].aggregate(pipeline)
    return source_generator.get(sources)


def get_works_by_person(
    person_id: str, query_params: QueryParams, pipeline_params: dict = None
) -> (Generator, int):
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
    ]
    if sort := query_params.sort:
        base_repository.set_sort(sort, pipeline)
    base_repository.set_pagination(pipeline, query_params)
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    cursor = database["works"].aggregate(pipeline)
    count_pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
        {"$count": "total_results"},
    ]
    total_results = next(database["works"].aggregate(count_pipeline), {"total_results": 0})[
        "total_results"
    ]
    return work_generator.get(cursor), total_results


def get_works_count_by_person(person_id) -> Optional[int]:
    return (
        database["works"]
        .aggregate([{"$match": {"authors.id": ObjectId(person_id)}}, {"$count": "total"}])
        .next()
        .get("total", 0)
    )


def get_sources_by_person(
    person_id: str, query_params, pipeline_params: dict | None = None
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = get_sources_by_person_pipeline(person_id)
    base_repository.set_match(pipeline, pipeline_params.get("match"))
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    cursor = database["works"].aggregate(pipeline)
    return source_generator.get(cursor)


def get_works_csv_by_person(person_id: str) -> Generator:
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "authors.affiliations.id",
                "foreignField": "_id",
                "as": "affiliations_data",
                "pipeline": [{"$project": {"id": "$_id", "addresses.country": 1, "ranking": 1}}],
            }
        },
        {
            "$lookup": {
                "from": "sources",
                "localField": "source.id",
                "foreignField": "_id",
                "as": "source_data",
                "pipeline": [
                    {
                        "$project": {
                            "external_urls": 1,
                            "ranking": 1,
                            "publisher": 1,
                            "apc": 1,
                        }
                    }
                ],
            }
        },
        {"$unwind": "$source_data"},
        {
            "$project": {
                "external_ids": 1,
                "authors": 1,
                "affiliations_data": 1,
                "bibliographic_info": 1,
                "citations_count": 1,
                "subjects": 1,
                "titles": 1,
                "types": 1,
                "source": 1,
                "source_data": 1,
                "year_published": 1,
                "ranking": 1,
                "abstract": 1,
            }
        },
    ]
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_csv_by_institution(institution_id: str) -> Generator:
    pipeline = [
        {"$match": {"authors.affiliations.id": ObjectId(institution_id)}},
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "authors.affiliations.id",
                "foreignField": "_id",
                "as": "affiliations_data",
                "pipeline": [{"$project": {"id": "$_id", "addresses.country": 1, "ranking": 1}}],
            }
        },
        {
            "$lookup": {
                "from": "sources",
                "localField": "source.id",
                "foreignField": "_id",
                "as": "source_data",
                "pipeline": [
                    {
                        "$project": {
                            "external_urls": 1,
                            "ranking": 1,
                            "publisher": 1,
                            "apc": 1,
                        }
                    }
                ],
            }
        },
        {"$unwind": "$source_data"},
        {
            "$project": {
                "external_ids": 1,
                "authors": 1,
                "affiliations_data": 1,
                "bibliographic_info": 1,
                "citations_count": 1,
                "subjects": 1,
                "titles": 1,
                "types": 1,
                "source": 1,
                "source_data": 1,
                "year_published": 1,
                "ranking": 1,
                "abstract": 1,
            }
        },
    ]
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_by_institution_or_group(
    affiliation_id: str, query_params: QueryParams, pipeline_params: dict
) -> (Generator, int):
    pipeline = [
        {"$match": {"authors.affiliations.id": ObjectId(affiliation_id)}},
    ]
    if sort := query_params.sort:
        base_repository.set_sort(sort, pipeline)
    base_repository.set_pagination(pipeline, query_params)
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    cursor = database["works"].aggregate(pipeline)
    count_pipeline = [
        {"$match": {"authors.affiliations.id": ObjectId(affiliation_id)}},
        {"$count": "total_results"},
    ]
    total_results = next(database["works"].aggregate(count_pipeline), {"total_results": 0})[
        "total_results"
    ]
    return work_generator.get(cursor), total_results


def get_works_by_faculty_or_department(
    affiliation_id: str, query_params: QueryParams, pipeline_params: dict
) -> (Generator, int):
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
        .get("relations", [])["id"]
    )
    pipeline = [
        {"$match": {"affiliations.id": ObjectId(affiliation_id)}},
        {"$project": {"_id": 1}},
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.id",
                "as": "work",
            }
        },
        {"$unwind": "$work"},
        {"$match": {"work.authors.affiliations.id": institution_id}},
        {"$replaceRoot": {"newRoot": "$work"}},
    ]
    if sort := query_params.sort:
        base_repository.set_sort(sort, pipeline)
    base_repository.set_pagination(pipeline, query_params)
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    cursor = database["person"].aggregate(pipeline)
    count_pipeline = [
        {"$match": {"authors.affiliations.id": ObjectId(affiliation_id)}},
        {"$count": "total_results"},
    ]
    total_results = next(database["person"].aggregate(count_pipeline), {"total_results": 0})[
        "total_results"
    ]
    return work_generator.get(cursor), total_results


def get_works_csv_by_group(group_id: str) -> Generator:
    pipeline = [
        {"$match": {"groups.id": ObjectId(group_id)}},
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "authors.affiliations.id",
                "foreignField": "_id",
                "as": "affiliations_data",
                "pipeline": [{"$project": {"id": "$_id", "addresses.country": 1, "ranking": 1}}],
            }
        },
        {
            "$lookup": {
                "from": "sources",
                "localField": "source.id",
                "foreignField": "_id",
                "as": "source_data",
                "pipeline": [
                    {
                        "$project": {
                            "external_urls": 1,
                            "ranking": 1,
                            "publisher": 1,
                            "apc": 1,
                        }
                    }
                ],
            }
        },
        {"$unwind": "$source_data"},
        {
            "$project": {
                "external_ids": 1,
                "authors": 1,
                "affiliations_data": 1,
                "bibliographic_info": 1,
                "citations_count": 1,
                "subjects": 1,
                "titles": 1,
                "types": 1,
                "source": 1,
                "source_data": 1,
                "year_published": 1,
                "ranking": 1,
                "abstract": 1,
            }
        },
    ]
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_csv_by_faculty_or_department(affiliation_id: str):
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
        .get("relations", [])["id"]
    )
    pipeline = [
        {"$match": {"affiliations.id": ObjectId(affiliation_id)}},
        {"$project": {"_id": 1}},
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.id",
                "as": "work",
                "pipeline": [
                    {
                        "$project": {
                            "external_ids": 1,
                            "authors": 1,
                            "bibliographic_info": 1,
                            "citations_count": 1,
                            "subjects": 1,
                            "titles": 1,
                            "types": 1,
                            "source": 1,
                            "year_published": 1,
                        }
                    }
                ],
            }
        },
        {"$unwind": "$work"},
        {"$match": {"work.authors.affiliations.id": ObjectId(institution_id)}},
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "work.authors.affiliations.id",
                "foreignField": "_id",
                "as": "affiliations_data",
                "pipeline": [{"$project": {"id": "$_id", "addresses.country": 1, "ranking": 1}}],
            }
        },
        {
            "$lookup": {
                "from": "sources",
                "localField": "work.source.id",
                "foreignField": "_id",
                "as": "source_data",
                "pipeline": [
                    {
                        "$project": {
                            "external_urls": 1,
                            "ranking": 1,
                            "publisher": 1,
                            "apc": 1,
                        }
                    }
                ],
            }
        },
        {"$unwind": "$source_data"},
        {
            "$project": {
                "external_ids": "$work.external_ids",
                "authors": "$work.authors",
                "affiliations_data": 1,
                "bibliographic_info": "$work.bibliographic_info",
                "citations_count": "$work.citations_count",
                "subjects": "$work.subjects",
                "titles": "$work.titles",
                "types": "$work.types",
                "source": "$work.source",
                "source_data": 1,
                "year_published": "$work.year_published",
                "ranking": "$work.ranking",
                "abstract": "$work.abstract",
            }
        },
    ]
    cursor = database["person"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_by_affiliation_pipeline(affiliation_id: str, affiliation_type: str):
    if affiliation_type == "institution":
        pipeline = [
            {
                "$match": {
                    "authors.affiliations.id": ObjectId(affiliation_id),
                },
            },
        ]
        return pipeline
    if affiliation_type == "group":
        pipeline = [
            {
                "$match": {
                    "groups.id": ObjectId(affiliation_id),
                },
            },
        ]
        return pipeline
    pipeline = [
        {"$match": {"_id": ObjectId(affiliation_id)}},
        {"$project": {"relations.types.type": 1, "relations.id": 1}},
        {"$unwind": "$relations"},
        {"$match": {"relations.types.type": "Education"}},
        {
            "$lookup": {
                "from": "person",
                "localField": "_id",
                "foreignField": "affiliations.id",
                "as": "person",
                "pipeline": [{"$project": {"id": 1, "full_name": 1}}],
            }
        },
        {"$unwind": "$person"},
        {
            "$lookup": {
                "from": "works",
                "localField": "person._id",
                "foreignField": "authors.id",
                "as": "work",
                "pipeline": [{"$project": {"authors": 1}}],
            }
        },
        {"$unwind": "$work"},
        {"$unwind": "$work.authors"},
        {"$match": {"$expr": {"$eq": ["$person._id", "$work.authors.id"]}}},
        {"$unwind": "$work.authors.affiliations"},
        {"$match": {"$expr": {"$eq": ["$relations.id", "$work.authors.affiliations.id"]}}},
        {"$group": {"_id": "$work._id", "work": {"$first": "$work"}}},
        {"$project": {"work._id": 1}},
        {
            "$lookup": {
                "from": "works",
                "localField": "work._id",
                "foreignField": "_id",
                "as": "works",
            }
        },
        {"$unwind": "$works"},
    ]
    return pipeline


def get_sources_by_affiliation_pipeline(affiliation_id, affiliation_type):
    pipeline = get_works_by_affiliation_pipeline(affiliation_id, affiliation_type)
    is_person = True if affiliation_type in ["faculty", "department"] else False
    pipeline += [
        {
            "$lookup": {
                "from": "sources",
                "localField": ("works.source.id" if is_person else "source.id"),
                "foreignField": "_id",
                "as": "source",
            }
        },
        {"$unwind": "$source"},
        {
            "$addFields": {
                "source.apc.year_published": (
                    "$works.year_published" if is_person else "$year_published"
                ),
                "source.date_published": (
                    "$works.date_published" if is_person else "$date_published"
                ),
            }
        },
        {"$replaceRoot": {"newRoot": "$source"}},
    ]
    return pipeline


def get_sources_by_person_pipeline(person_id):
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
        {
            "$lookup": {
                "from": "sources",
                "localField": "source.id",
                "foreignField": "_id",
                "as": "source",
            }
        },
        {"$unwind": "$source"},
        {
            "$addFields": {
                "source.apc.year_published": "$year_published",
                "source.date_published": "$date_published",
            }
        },
        {"$replaceRoot": {"newRoot": "$source"}},
    ]
    return pipeline


def get_works_count_by_faculty_or_department(affiliation_id: str) -> int:
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
        .get("relations", [])["id"]
    )
    pipeline = [
        {"$match": {"affiliations.id": ObjectId(affiliation_id)}},
        {"$project": {"_id": 1}},
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.id",
                "as": "works",
                "pipeline": [
                    {"$match": {"authors.affiliations.id": institution_id}},
                    {"$count": "count"},
                ],
            }
        },
        {"$addFields": {"products_count": {"$ifNull": [{"$arrayElemAt": ["$works.count", 0]}, 0]}}},
    ]
    result = next(database["person"].aggregate(pipeline), {"products_count": 0})
    return result.get("products_count", 0)
