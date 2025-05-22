from typing import Generator


from domain.models.base_model import QueryParams
from infrastructure.generators import work_generator
from infrastructure.mongo import database
from infrastructure.repositories import work_repository


def get_works_csv_by_person(person_id: str, query_params: QueryParams) -> Generator:
    pipeline = [
        {"$match": {"authors.id": person_id}},
    ]
    work_repository.set_product_filters(pipeline, query_params)
    pipeline += [
        {
            "$lookup": {
                "from": "affiliations",  # type: ignore
                "localField": "authors.affiliations.id",  # type: ignore
                "foreignField": "_id",  # type: ignore
                "as": "affiliations_data",  # type: ignore
                "pipeline": [{"$project": {"id": "$_id", "addresses.country": 1, "ranking": 1}}],  # type: ignore
            }
        },
        {
            "$lookup": {
                "from": "sources",  # type: ignore
                "localField": "source.id",  # type: ignore
                "foreignField": "_id",  # type: ignore
                "as": "source_data",  # type: ignore
                "pipeline": [  # type: ignore
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
        {
            "$project": {
                "external_ids": 1,  # type: ignore
                "authors": 1,  # type: ignore
                "affiliations_data": 1,  # type: ignore
                "bibliographic_info": 1,  # type: ignore
                "citations_count": 1,  # type: ignore
                "open_access": 1,  # type: ignore
                "subjects": 1,  # type: ignore
                "titles": 1,  # type: ignore
                "types": 1,  # type: ignore
                "source": 1,  # type: ignore
                "source_data": 1,  # type: ignore
                "year_published": 1,  # type: ignore
                "ranking": 1,  # type: ignore
                "abstract": 1,  # type: ignore
            }
        },
    ]
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_csv_by_affiliation(affiliation_id: str, query_params: QueryParams) -> Generator:
    pipeline = [
        {"$match": {"authors.affiliations.id": affiliation_id}},
    ]
    work_repository.set_product_filters(pipeline, query_params)
    pipeline += [
        {
            "$lookup": {
                "from": "affiliations",  # type: ignore
                "localField": "authors.affiliations.id",  # type: ignore
                "foreignField": "_id",  # type: ignore
                "as": "affiliations_data",  # type: ignore
                "pipeline": [{"$project": {"id": "$_id", "addresses.country": 1, "ranking": 1}}],  # type: ignore
            }
        },
        {
            "$lookup": {
                "from": "sources",  # type: ignore
                "localField": "source.id",  # type: ignore
                "foreignField": "_id",  # type: ignore
                "as": "source_data",  # type: ignore
                "pipeline": [  # type: ignore
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
        {
            "$project": {
                "external_ids": 1,  # type: ignore
                "authors": 1,  # type: ignore
                "affiliations_data": 1,  # type: ignore
                "bibliographic_info": 1,  # type: ignore
                "open_access": 1,  # type: ignore
                "citations_count": 1,  # type: ignore
                "subjects": 1,  # type: ignore
                "titles": 1,  # type: ignore
                "types": 1,  # type: ignore
                "source": 1,  # type: ignore
                "source_data": 1,  # type: ignore
                "year_published": 1,  # type: ignore
                "ranking": 1,  # type: ignore
                "abstract": 1,  # type: ignore
            }
        },
    ]
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)
