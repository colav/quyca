from typing import Any, Generator, Tuple
from bson import ObjectId

from infrastructure.mongo import database
from infrastructure.repositories import base_repository
from infrastructure.generators import source_generator
from domain.models.source_model import Source
from domain.exceptions.not_entity_exception import NotEntityException
from quyca.domain.constants.source_types import NORMALIZED_TYPE_MAPPING
from quyca.domain.models.base_model import QueryParams


def get_source_by_id(source_id: str) -> Source:
    """
    Parameters:
    -----------
    source_id : str
        The unique identifier of the source to be retrieved.
    Returns:
    --------
    Source
        The Source object corresponding to the provided source_id.
    Raises:
    -------
    NotEntityException
        If no source with the given source_id exists in the database.
    """
    source_object_id = ObjectId(source_id)
    source_data = database["sources"].find_one({"_id": source_object_id})
    if not source_data:
        raise NotEntityException(f"The source with id {source_id} does not exist.")

    works_count = database["works"].count_documents({"source.id": source_object_id})
    if works_count == 0:
        source_data["topics"] = []
        return Source(**source_data)

    topics_limit = works_count * 0.02
    pipeline = [
        {"$match": {"source.id": source_object_id}},
        {"$project": {"_id": 0, "primary_topic": 1}},
        {"$match": {"primary_topic": {"$exists": True, "$ne": None}}},
        {"$group": {"_id": "$primary_topic.id", "count": {"$sum": 1}, "topic": {"$first": "$primary_topic"}}},
        {"$match": {"count": {"$gte": topics_limit}}},
        {
            "$project": {
                "_id": 0,
                "id": "$topic.id",
                "display_name": "$topic.display_name",
                "subfield": "$topic.subfield",
                "field": "$topic.field",
                "domain": "$topic.domain",
            }
        },
    ]

    topics = list(database["works"].aggregate(pipeline))
    source_data["topics"] = topics

    return Source(**source_data)


def search_sources(query_params: QueryParams, pipeline_params: dict) -> Tuple[Generator, int]:
    """
    Parameters:
    -----------
    query_params : QueryParams
        The query parameters containing keywords and other filters for the search.
    pipeline_params : dict
        The pipeline parameters for the MongoDB aggregation pipeline.

    Returns:
    --------
    Tuple[Generator, int]
        A tuple containing a generator for the search results and the total number of results.
    """
    pipeline: list[dict[str, Any]] = []
    if query_params.keywords:
        pipeline.append({"$match": {"$text": {"$search": query_params.keywords}}})
    set_source_filters(pipeline, query_params)
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    raw_sources = database["sources"].aggregate(pipeline)

    # Topics for each source
    sources = [Source(**source) for source in raw_sources]
    for source in sources:
        s_id = ObjectId(source.id)
        works_count = database["works"].count_documents({"source.id": s_id})
        if works_count == 0:
            source.topics = []
            continue
        topics_limit = works_count * 0.02
        topic_pipeline = [
            {"$match": {"source.id": s_id, "primary_topic": {"$exists": True, "$ne": None}}},
            {"$project": {"_id": 0, "primary_topic": 1}},
            {"$group": {"_id": "$primary_topic.id", "count": {"$sum": 1}, "topic": {"$first": "$primary_topic"}}},
            {"$match": {"count": {"$gte": topics_limit}}},
            {
                "$project": {
                    "_id": 0,
                    "id": "$topic.id",
                    "display_name": "$topic.display_name",
                    "subfield": "$topic.subfield",
                    "field": "$topic.field",
                    "domain": "$topic.domain",
                }
            },
        ]
        source.topics = list(database["works"].aggregate(topic_pipeline))

    count_pipeline: list[dict[str, Any]] = []
    if query_params.keywords:
        count_pipeline.append({"$match": {"$text": {"$search": query_params.keywords}}})
    set_source_filters(count_pipeline, query_params)

    count_pipeline += [{"$count": "total_results"}]
    total_results = next(database["sources"].aggregate(count_pipeline), {"total_results": 0})["total_results"]
    return source_generator.generate_sources(sources), total_results


def get_search_sources_available_filters(query_params: QueryParams) -> dict:
    """
    Parameters:
    -----------
    query_params : QueryParams
        The query parameters containing keywords and other filters for the search.

    Returns:
    --------
    dict
        A dictionary containing the available filters for the search.
    """
    pipeline: list[dict[str, Any]] = []
    if query_params.keywords:
        pipeline.append({"$match": {"$text": {"$search": query_params.keywords}}})
    set_source_filters(pipeline, query_params)

    pipeline += [
        {
            "$facet": {
                "source_types": [
                    {"$project": {"types": 1}},
                    {"$unwind": "$types"},
                    {"$group": {"_id": {"source": "$types.source", "type": "$types.type"}, "count": {"$sum": 1}}},
                    {"$group": {"_id": "$_id.source", "types": {"$push": {"type": "$_id.type", "count": "$count"}}}},
                ],
                "scimago_quartiles": [
                    {"$project": {"ranking": 1}},
                    {
                        "$match": {
                            "ranking": {
                                "$elemMatch": {
                                    "source": {"$in": ["scimago Best Quartile", "Scimago Best Quartile"]},
                                    "rank": {"$in": ["Q1", "Q2", "Q3", "Q4", "-"]},
                                }
                            }
                        }
                    },
                    {"$unwind": "$ranking"},
                    {
                        "$match": {
                            "ranking.source": {"$in": ["scimago Best Quartile", "Scimago Best Quartile"]},
                            "ranking.rank": {"$exists": True, "$nin": [None, ""]},
                        }
                    },
                    {"$sort": {"_id": 1, "ranking.to_date": -1}},
                    {"$group": {"_id": "$_id", "current_quartile": {"$first": "$ranking.rank"}}},
                    {"$match": {"current_quartile": {"$in": ["Q1", "Q2", "Q3", "Q4", "-"]}}},
                    {"$group": {"_id": "$current_quartile", "count": {"$sum": 1}}},
                    {"$sort": {"_id": 1}},
                ],
            }
        }
    ]

    available_filters: dict = next(database["sources"].aggregate(pipeline), {})
    return available_filters


def set_source_filters(pipeline: list, query_params: QueryParams) -> None:
    set_source_types(pipeline, query_params.source_types)
    set_scimago_quartiles(pipeline, query_params.scimago_quartiles)


def set_source_types(pipeline: list, type_filters: str | None) -> None:
    """
    It takes a comma-separated string of source types, splits it into a list, and adds a match stage to the pipeline.

    E.g {"$match": {"types.type": {"$in": ["journal", "repository"]}}}
    """
    if not type_filters:
        return

    source_types = []
    for type in type_filters.split(","):
        type = type.strip().lower()
        if not type:
            continue
        mapped = NORMALIZED_TYPE_MAPPING.get(type, None)
        if mapped:
            source_types.append(mapped)

    if source_types:
        pipeline.append({"$match": {"types.type": {"$in": source_types}}})


def set_scimago_quartiles(pipeline: list, quartile_filters: str | None) -> None:
    """
    Filters sources by their current Scimago Best Quartile ranking.

    E.g {"$match": {"ranking": {"$elemMatch": {"source": {"$in": ["scimago Best Quartile", "Scimago Best Quartile"]}, "rank": {"$in": ["Q1", "Q2"]}}}}}
    """
    if not quartile_filters:
        return

    quartiles = []
    for quartile in quartile_filters.split(","):
        quartile = quartile.strip()
        if quartile in ["Q1", "Q2", "Q3", "Q4", "-"]:
            quartiles.append(quartile)

    if not quartiles:
        return

    pipeline.append(
        {
            "$match": {
                "ranking": {
                    "$elemMatch": {
                        "source": {"$in": ["scimago Best Quartile", "Scimago Best Quartile"]},
                        "rank": {"$in": quartiles},
                    }
                }
            }
        }
    )
