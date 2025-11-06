from typing import Any, Dict, Generator, List


from quyca.domain.models.base_model import QueryParams
from quyca.infrastructure.generators import work_generator
from quyca.infrastructure.mongo import database
from quyca.infrastructure.repositories import work_repository


def get_works_csv_by_person(person_id: str, query_params: QueryParams) -> Generator:
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"authors.id": person_id}},
    ]
    work_repository.set_product_filters(pipeline, query_params)
    pipeline += [
        {
            "$project": {
                "external_ids": 1,
                "authors": 1,
                "bibliographic_info": 1,
                "open_access": 1,
                "citations_count": 1,
                "subjects": 1,
                "titles": 1,
                "types": 1,
                "source": 1,
                "groups": 1,
                "year_published": 1,
                "ranking": 1,
                "primary_topic": 1,
                "doi": 1,
            }
        },
    ]
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_csv_by_affiliation(affiliation_id: str, query_params: QueryParams, affiliation_type: str) -> Generator:
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"authors.affiliations.id": affiliation_id, "authors.affiliations.types.type": affiliation_type}},
    ]
    work_repository.set_product_filters(pipeline, query_params)
    pipeline += [
        {
            "$project": {
                "external_ids": 1,
                "authors": 1,
                "bibliographic_info": 1,
                "open_access": 1,
                "citations_count": 1,
                "subjects": 1,
                "titles": 1,
                "types": 1,
                "source": 1,
                "groups": 1,
                "year_published": 1,
                "ranking": 1,
                "primary_topic": 1,
                "doi": 1,
            }
        }
    ]
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)
