from typing import Any, Dict, Dict, List

from quyca.domain.models.base_model import QueryParams


def set_geo_filters(query_params: QueryParams, geo_type: str) -> List[Dict[str, Any]]:
    pipeline: List[Dict[str, Any]] = (
        [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    )
    pipeline.append({"$match": {"type": geo_type}})

    states = []
    if query_params.states:
        for state in query_params.states:
            states.append(state)

    if geo_type == "cities" and states:
        pipeline.append({"$match": {"state.id": {"$in": states}}})
    return pipeline
