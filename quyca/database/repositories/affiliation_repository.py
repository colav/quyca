from typing import Generator

from bson import ObjectId

from database.models.base_model import QueryParams
from constants.institutions import institutions_list
from database.generators import affiliation_generator
from database.models.affiliation_model import Affiliation
from database.repositories import base_repository
from database.mongo import database
from exceptions.not_entity_exception import NotEntityException


def get_affiliation_by_id(affiliation_id: str) -> Affiliation:
    affiliation_data = database["affiliations"].find_one({"_id": ObjectId(affiliation_id)})
    if not affiliation_data:
        raise NotEntityException(f"The affiliation with id {affiliation_id} does not exist.")
    return Affiliation(**affiliation_data)


def get_groups_by_affiliation(affiliation_id: str, affiliation_type: str):
    pipeline = get_groups_by_affiliation_pipeline(affiliation_id, affiliation_type)
    collection = "person" if affiliation_type in ["faculty", "department"] else "affiliations"
    groups = database[collection].aggregate(pipeline)
    return affiliation_generator.get(groups)


def get_groups_by_affiliation_pipeline(affiliation_id: str, affiliation_type: str) -> list:
    if affiliation_type == "group":
        return [{"$match": {"_id": ObjectId(affiliation_id)}}]
    if affiliation_type in ["department", "faculty"]:
        return [
            {"$match": {"affiliations.id": ObjectId(affiliation_id)}},
            {"$project": {"affiliations": 1}},
            {"$unwind": "$affiliations"},
            {"$match": {"affiliations.types.type": "group"}},
            {"$project": {"aff_id": "$affiliations.id"}},
            {
                "$lookup": {
                    "from": "affiliations",
                    "localField": "aff_id",
                    "foreignField": "_id",
                    "as": "affiliation",
                }
            },
            {"$unwind": "$affiliation"},
            {
                "$group": {
                    "_id": "$aff_id",
                    "affiliation": {"$addToSet": "$affiliation"},
                }
            },
            {"$unwind": "$affiliation"},
            {"$project": {"_id": 0, "affiliation": 1}},
            {"$replaceRoot": {"newRoot": "$affiliation"}},
        ]
    return [
        {
            "$match": {
                "relations.id": ObjectId(affiliation_id),
                "types.type": "group",
            }
        }
    ]


def get_related_affiliations_by_type(
    affiliation_id: str, affiliation_type: str, relation_type: str
) -> Generator:
    pipeline = get_related_affiliations_by_type_pipeline(
        affiliation_id, affiliation_type, relation_type
    )
    if relation_type == "group" and affiliation_type in ["faculty", "department"]:
        collection = "person"
    else:
        collection = "affiliations"
    affiliations = database[collection].aggregate(pipeline)
    return affiliation_generator.get(affiliations)


def get_related_affiliations_by_type_pipeline(
    affiliation_id: str, affiliation_type: str, relation_type: str
) -> list:
    if relation_type == "group":
        return get_groups_by_affiliation_pipeline(affiliation_id, affiliation_type)
    return [
        {
            "$match": {
                "relations.id": ObjectId(affiliation_id),
                "types.type": relation_type,
            }
        }
    ]


def search_affiliations(
    affiliation_type: str,
    query_params: QueryParams,
    pipeline_params: dict | None = None,
) -> (Generator, int):
    types = institutions_list if affiliation_type == "institution" else [affiliation_type]
    pipeline = (
        [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    )
    pipeline += [
        {
            "$match": {
                "types.type": {"$in": types},
            }
        },
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.affiliations.id",
                "as": "works",
                "pipeline": [{"$count": "count"}],
            }
        },
        {
            "$addFields": {
                "products_count": {"$ifNull": [{"$arrayElemAt": ["$works.count", 0]}, 0]},
            },
        },
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "relations.id",
                "foreignField": "_id",
                "as": "relations_data",
                "pipeline": [{"$project": {"id": "$_id", "external_urls": 1}}],
            }
        },
        {"$project": {"works": 0}},
    ]
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    affiliations = database["affiliations"].aggregate(pipeline)
    count_pipeline = (
        [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    )
    count_pipeline += [
        {"$match": {"types.type": {"$in": types}}},
        {"$count": "total_results"},
    ]
    total_results = next(database["affiliations"].aggregate(count_pipeline), {"total_results": 0})[
        "total_results"
    ]
    return affiliation_generator.get(affiliations), total_results
