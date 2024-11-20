from typing import Generator, Tuple


from domain.models.base_model import QueryParams
from domain.constants.institutions import institutions_list
from infrastructure.generators import affiliation_generator
from domain.models.affiliation_model import Affiliation
from infrastructure.repositories import base_repository
from infrastructure.mongo import database
from infrastructure.repositories.base_repository import set_project
from domain.exceptions.not_entity_exception import NotEntityException


def get_affiliation_by_id(affiliation_id: str) -> Affiliation:
    pipeline = [
        {"$match": {"hash": affiliation_id}},
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "relations.hash",
                "foreignField": "hash",
                "as": "relations_data",
                "pipeline": [{"$project": {"hash": 1, "external_urls": 1}}],
            }
        },
    ]
    try:
        affiliation_data = database["affiliations"].aggregate(pipeline).next()
    except:
        raise NotEntityException(f"The affiliation with id {affiliation_id} does not exist.")
    return Affiliation(**affiliation_data)


def get_affiliations_by_institution(institution_id: str, relation_type: str) -> Generator:
    pipeline = [
        {
            "$match": {
                "relations.hash": institution_id,
                "types.type": relation_type,
            }
        }
    ]
    set_project(pipeline, ["hash", "names"])
    affiliations = database["affiliations"].aggregate(pipeline)
    return affiliation_generator.get(affiliations)


def get_departments_by_faculty(faculty_id: str) -> Generator:
    return get_affiliations_by_institution(faculty_id, "department")


def get_groups_by_faculty_or_department(affiliation_id: str) -> Generator:
    institution_id = (
        database["affiliations"]
        .aggregate(
            [
                {"$match": {"hash": affiliation_id}},
                {"$unwind": "$relations"},
                {"$match": {"relations.types.type": "education"}},
            ]
        )
        .next()
        .get("relations", {})
        .get("hash", None)
    )
    pipeline = [
        {
            "$match": {
                "affiliations.hash": affiliation_id,
            }
        },
        {"$unwind": "$affiliations"},
        {"$match": {"affiliations.types.type": "group"}},
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "affiliations.id",
                "foreignField": "_id",
                "as": "group",
                "pipeline": [
                    {
                        "$match": {
                            "relations.hash": institution_id,
                            "types.type": "group",
                        },
                    },
                    {"$project": {"_id": 1, "hash": 1, "names": 1}},
                ],
            }
        },
        {"$unwind": "$group"},
        {"$group": {"_id": "$group.hash", "names": {"$first": "$group.names"}, "hash": {"$first": "$group.hash"}}},
    ]
    groups = database["person"].aggregate(pipeline)
    list_groups = list(groups)
    return affiliation_generator.get(groups)


def search_affiliations(
    affiliation_type: str,
    query_params: QueryParams,
    pipeline_params: dict | None = None,
) -> Tuple[Generator, int]:
    types = institutions_list if affiliation_type == "institution" else [affiliation_type]
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    pipeline += [
        {
            "$match": {
                "types.type": {"$in": types},
            }
        },
        {
            "$lookup": {
                "from": "affiliations",  # type: ignore
                "localField": "relations.hash",  # type: ignore
                "foreignField": "hash",  # type: ignore
                "as": "relations_data",  # type: ignore
                "pipeline": [{"$project": {"hash": 1, "external_urls": 1}}],  # type: ignore
            }
        },
        {"$project": {"works": 0}},  # type: ignore
    ]
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    affiliations = database["affiliations"].aggregate(pipeline)
    count_pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    count_pipeline += [
        {"$match": {"types.type": {"$in": types}}},
        {"$count": "total_results"},  # type: ignore
    ]
    total_results = next(database["affiliations"].aggregate(count_pipeline), {"total_results": 0})["total_results"]
    return affiliation_generator.get(affiliations), total_results
