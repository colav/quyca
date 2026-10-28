from typing import Any, Dict, Generator, Iterable, List, Mapping, Sequence
from bson import ObjectId

from quyca.generators import person_generator
from quyca.models.base_model import ExternalId
from quyca.repositories import base_repository
from quyca.exceptions.not_entity_exception import NotEntityException
from quyca.models.person_model import Person
from quyca.clients.mongo import database


def get_person_by_id(person_id: str, pipeline_params: dict) -> Person:
    old_id = None
    try:
        old_id = ObjectId(person_id)
    except Exception:
        pass

    match_stage = {"$match": {"$or": [{"_id": person_id}] + ([{"_id_old": old_id}] if old_id else [])}}

    pipeline: List[Dict[str, Any]] = [
        match_stage,
        {
            "$addFields": {
                "filtered_affiliations": {
                    "$filter": {
                        "input": "$affiliations",
                        "as": "affiliation",
                        "cond": {"$eq": ["$$affiliation.end_date", -1]},
                    }
                }
            }
        },
        {
            "$addFields": {
                "logo": {
                    "$arrayElemAt": [
                        {
                            "$map": {
                                "input": {
                                    "$filter": {
                                        "input": {
                                            "$reduce": {
                                                "input": "$affiliations",
                                                "initialValue": [],
                                                "in": {
                                                    "$concatArrays": [
                                                        "$$value",
                                                        {"$ifNull": ["$$this.external_urls", []]},
                                                    ]
                                                },
                                            }
                                        },
                                        "as": "ext",
                                        "cond": {"$eq": ["$$ext.source", "logo"]},
                                    }
                                },
                                "as": "logo_item",
                                "in": "$$logo_item.url",
                            }
                        },
                        0,
                    ]
                }
            }
        },
    ]

    base_repository.set_project(pipeline, pipeline_params.get("project"))

    person_cursor = database["person"].aggregate(pipeline)
    person_data: Dict[str, Any] | None = next(person_cursor, None)
    if not person_data:
        raise NotEntityException(f"The person with id {person_id} does not exist.")
    return Person(**person_data)


def get_persons_by_affiliation(affiliation_id: str) -> Generator:
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"affiliations.id": affiliation_id}},
        {"$sort": {"products_count": -1}},
        {"$project": {"_id": 1, "full_name": 1}},
    ]
    cursor = database["person"].aggregate(pipeline)
    return person_generator.get(cursor)


def get_person_external_ids(person_id: str) -> list[ExternalId]:
    match = {"$match": {"_id": person_id}}

    pipeline: Sequence[Mapping[str, Any]] = [
        match,
        {"$project": {"external_ids": 1}},
    ]

    cursor = database["person"].aggregate(pipeline)
    data = next(cursor, None)

    if not data:
        return []

    return [ExternalId(**eid) for eid in data.get("external_ids", [])]


def get_affiliation_years(person_ids: Iterable[str]) -> Dict[str, Dict[str, List[int]]]:
    ids = list({pid for pid in person_ids if pid})
    if not ids:
        return {}
    cursor = database["person"].find(
        {"_id": {"$in": ids}},
        {"affiliations.id": 1, "affiliations.years": 1},
    )
    return {
        person["_id"]: {aff["id"]: aff.get("years") or [] for aff in person.get("affiliations", []) if aff.get("id")}
        for person in cursor
    }
