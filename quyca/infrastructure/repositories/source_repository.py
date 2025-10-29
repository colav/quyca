from typing import Dict, Generator, List, Tuple
from bson import ObjectId

from infrastructure.mongo import database
from infrastructure.repositories import base_repository
from infrastructure.generators import source_generator
from domain.models.source_model import Source
from domain.exceptions.not_entity_exception import NotEntityException
from quyca.domain.models.base_model import QueryParams
from quyca.domain.constants.clean_source import source_type_mapping


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
    source_data = database["sources"].find_one({"_id": ObjectId(source_id)})
    if not source_data:
        raise NotEntityException(f"The source with id {source_id} does not exist.")
    return Source(**source_data)


def search_sources(query_params: QueryParams, pipeline_params: Dict) -> Tuple[Generator, int]:
    """
    Parameters:
    -----------
    query_params : QueryParams
        The query parameters containing keywords and other filters for the search.
    pipeline_params : Dict
        The pipeline parameters for the MongoDB aggregation pipeline.

    Returns:
    --------
    Tuple[Generator, int]
        A tuple containing a generator for the search results and the total number of results.
    """
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    set_source_filters(pipeline, query_params)
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    sources = database["sources"].aggregate(pipeline)

    count_pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    set_source_filters(count_pipeline, query_params)

    count_pipeline += [{"$count": "total_results"}]
    total_results = next(database["sources"].aggregate(count_pipeline), {"total_results": 0})["total_results"]
    return source_generator.get(sources), total_results


def set_source_filters(pipeline: List, query_params: QueryParams) -> None:
    set_source_types(pipeline, query_params.source_types)


def set_source_types(pipeline: List, type_filters: str | None) -> None:
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
        mapped = source_type_mapping.get(type, None)
        if mapped:
            source_types.append(mapped)

    if source_types:
        pipeline.append({"$match": {"types.type": {"$in": source_types}}})
