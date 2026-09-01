from typing import Any, Generator, Mapping, Tuple


from quyca.domain.models.base_model import QueryParams
from quyca.domain.constants.institutions import institutions_list
from quyca.domain.models.affiliation_model import Affiliation
from quyca.infrastructure.repositories import base_repository
from quyca.infrastructure.mongo import database
from quyca.infrastructure.repositories.base_repository import set_project
from quyca.domain.exceptions.not_entity_exception import NotEntityException
from quyca.infrastructure.generators import affiliation_generator


def get_affiliation_by_id(affiliation_id: str) -> Affiliation:
    pipeline: list[Mapping[str, Any]] = [{"$match": {"_id": affiliation_id}}, {"$project": {"works": 0}}]
    try:
        affiliation_data = database["affiliations"].aggregate(pipeline).next()
    except:
        raise NotEntityException(f"The affiliation with id {affiliation_id} does not exist.")
    return Affiliation(**affiliation_data)


def get_affiliations_by_institution(institution_id: str, relation_type: str) -> Generator[Affiliation, None, None]:
    pipeline = [
        {
            "$match": {
                "relations.id": institution_id,
                "types.type": relation_type,
            }
        }
    ]
    set_project(pipeline, ["_id", "names"])
    affiliations = database["affiliations"].aggregate(pipeline)
    return affiliation_generator.get(affiliations)


def get_departments_by_faculty(faculty_id: str) -> Generator:
    return get_affiliations_by_institution(faculty_id, "department")


def get_groups_by_faculty_or_department(affiliation_id: str) -> Generator[Affiliation, None, None]:
    institution_id = (
        database["affiliations"]
        .aggregate(
            [
                {"$match": {"_id": affiliation_id}},
                {"$unwind": "$relations"},
                {"$match": {"relations.types.type": "education"}},
            ]
        )
        .next()
        .get("relations", {})
        .get("id", None)
    )
    pipeline: list[Mapping[str, Any]] = [
        {
            "$match": {
                "affiliations.id": affiliation_id,
            }
        },
        {"$unwind": "$affiliations"},
        {
            "$match": {
                "affiliations.types.type": "group",
                "affiliations.relations.id": institution_id,
            }
        },
        {"$group": {"_id": "$affiliations.id", "names": {"$push": "$affiliations.name"}}},
    ]
    groups = database["person"].aggregate(pipeline)
    return affiliation_generator.get(groups)


def search_affiliations(
    affiliation_type: str,
    query_params: QueryParams,
    pipeline_params: dict | None = None,
) -> Tuple[Generator, int]:
    types = institutions_list if affiliation_type == "institution" else [affiliation_type]
    pipeline: list[dict[str, Any]] = []

    if query_params.keywords:
        pipeline.append({"$match": {"$text": {"$search": query_params.keywords}}})

    pipeline += [
        {
            "$match": {
                "types.type": {"$in": types},
            }
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
    ]
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    affiliations = database["affiliations"].aggregate(pipeline)

    count_pipeline: list[dict[str, Any]] = []
    if query_params.keywords:
        count_pipeline.append({"$match": {"$text": {"$search": query_params.keywords}}})
    count_pipeline += [
        {"$match": {"types.type": {"$in": types}}},
        {"$count": "total_results"},
    ]
    total_results = next(database["affiliations"].aggregate(count_pipeline), {"total_results": 0})["total_results"]
    return affiliation_generator.get(affiliations), total_results


def get_search_affiliations_available_filters(
    affiliation_type: str,
    query_params: QueryParams,
) -> dict:
    types = institutions_list if affiliation_type == "institution" else [affiliation_type]
    pipeline: list[dict[str, Any]] = []
    if query_params.keywords:
        pipeline.append({"$match": {"$text": {"$search": query_params.keywords}}})

    pipeline = [
        {"$match": {"types.type": affiliation_type}},
        {
            "$facet": {
                "states": [
                    {"$project": {"_id": 1, "addresses.state": 1}},
                    {"$match": {"addresses.state": {"$exists": True, "$ne": ""}}},
                    {"$unwind": "$addresses"},
                    {"$match": {"addresses.state": {"$exists": True, "$ne": ""}}},
                    {"$group": {"_id": {"affiliation_id": "$_id", "state": "$addresses.state"}}},
                    {"$group": {"_id": "$_id.state", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ],
                "cities": [
                    {"$project": {"_id": 1, "addresses.city": 1}},
                    {"$match": {"addresses.city": {"$exists": True, "$ne": ""}}},
                    {"$unwind": "$addresses"},
                    {"$match": {"addresses.city": {"$exists": True, "$ne": ""}}},
                    {"$group": {"_id": {"affiliation_id": "$_id", "city": "$addresses.city"}}},
                    {"$group": {"_id": "$_id.city", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ],
            }
        },
    ]

    available_filters: dict = next(database["affiliations"].aggregate(pipeline), {})
    return available_filters
