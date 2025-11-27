from infrastructure.mongo import database as db
from infrastructure.generators import news_generator
from infrastructure.repositories import base_repository
from typing import Generator, Optional, Set, Iterable, Any
from domain.models.base_model import QueryParams


def cc_from_person(person_id: str) -> Optional[str]:
    """
    Retrieves the national ID (Cédula de Ciudadanía) for a given person.

    Searches the `person` collection for the external ID of type "Cédula de Ciudadanía".

    Parameters:
    -----------
    person_id : str
        The ID of the person in the database.

    Returns:
    --------
    Optional[str]
        The national ID (CC) if found, otherwise None.
    """
    doc = db.person.find_one(
        {
            "_id": person_id,
            "external_ids.source": {"$in": ["Cédula de Ciudadanía", "Cédula de Extranjería", "Pasaporte", "Passport"]},
        },
        {"external_ids.$": 1},
    )
    if doc and doc.get("external_ids"):
        return str(doc["external_ids"][0]["id"])
    return None


def author_ids_for_affiliation(_db: Any, affiliation_id: str) -> Set[str]:
    """
    Retrieves a set of author IDs associated with a specific affiliation.
    Queries the `person` collection for distinct IDs of authors who have
    the specified affiliation and have an external ID of type "Cédula de Ciudadanía",
    "Cédula de Extranjería", "Pasaporte", or "Passport".

    Parameters:
    -----------
    _db : database
        The database instance to query.
    affiliation_id : str
        The ID of the affiliation for which author IDs are being retrieved.

    Returns:
    --------
    Set[str]
        A set of author IDs associated with the specified affiliation.
    """
    ids_iter: Iterable[Any] = _db["person"].distinct(
        "_id",
        {
            "affiliations.id": affiliation_id,
            "external_ids.source": {
                "$in": [
                    "Cédula de Ciudadanía",
                    "Cédula de Extranjería",
                    "Pasaporte",
                    "Passport",
                ]
            },
        },
    )
    return {str(i) for i in ids_iter if i is not None}


def get_news_by_person(person_id: str, query_params: QueryParams) -> Generator:
    """
    Retrieves news entries related to a given person as a generator.

    Builds an aggregation pipeline to join news data (from media and URL collections)
    associated with the person's national ID and yields News objects.

    Parameters:
    -----------
    person_id : str
        The ID of the person whose news entries are being retrieved.
    query_params : QueryParams
        Query parameters for pagination and sorting.

    Yields:
    -------
    News
        News model instances generated from the aggregated results.
    """
    cc = cc_from_person(person_id)
    if not cc:
        yield []

    pipeline = [
        {"$match": {"professor_id": cc}},
        {"$unwind": "$classified_urls_ids"},
        {
            "$lookup": {
                "from": "news_urls_collection",
                "localField": "classified_urls_ids",
                "foreignField": "url_id",
                "as": "url_docs",
            }
        },
        {"$unwind": "$url_docs"},
        {
            "$lookup": {
                "from": "news_media_collection",
                "localField": "url_docs.medium_id",
                "foreignField": "medium_id",
                "as": "medium_docs",
            }
        },
        {"$unwind": "$medium_docs"},
        {"$replaceRoot": {"newRoot": {"$mergeObjects": ["$url_docs", {"medium": "$medium_docs.medium"}]}}},
    ]

    if sort := query_params.sort:
        if sort == "alphabetical_asc":
            pipeline.append({"$sort": {"url_title": 1}})
        if sort == "year_desc":
            pipeline.append({"$sort": {"url_date": -1}})

    base_repository.set_pagination(pipeline, query_params)
    cursor = db.news_professors_collection.aggregate(pipeline, allowDiskUse=True)
    yield from news_generator.get(cursor)


def news_count_by_person(person_id: str) -> int:
    """
    Counts the number of news entries associated with a given person.

    Executes an aggregation pipeline to compute the total number of news
    records linked to the person via their national ID.

    Parameters:
    -----------
    person_id : str
        The ID of the person whose news entries are to be counted.

    Returns:
    --------
    int
        Total number of matching news entries.
    """
    cc = cc_from_person(person_id)
    if not cc:
        return 0

    pipeline = [
        {"$match": {"professor_id": cc}},
        {"$unwind": "$classified_urls_ids"},
        {
            "$lookup": {
                "from": "news_urls_collection",
                "localField": "classified_urls_ids",
                "foreignField": "url_id",
                "as": "url_docs",
            }
        },
        {"$unwind": "$url_docs"},
        {
            "$lookup": {
                "from": "news_media_collection",
                "localField": "url_docs.medium_id",
                "foreignField": "medium_id",
                "as": "medium_docs",
            }
        },
        {"$unwind": "$medium_docs"},
        {"$count": "total"},
    ]
    result = list(db.news_professors_collection.aggregate(pipeline))
    return int(result[0]["total"]) if result else 0


def get_news_by_affiliation(affiliation_id: str, affiliation_type: str, query_params: QueryParams) -> Generator:
    """
    Retrieves news entries related to a given affiliation as a generator.
    Builds an aggregation pipeline to join news data (from media and URL collections)
    associated with authors linked to the affiliation and yields News objects.
    Parameters:
    -----------
    affiliation_id : str
        The ID of the affiliation whose news entries are being retrieved.
    affiliation_type : str
        The type of the affiliation (e.g., "institution", "department").
    query_params : QueryParams
        Query parameters for pagination and sorting.
    Yields:
    -------
    News
        News model instances generated from the aggregated results.
    """
    authors_ids = author_ids_for_affiliation(db, affiliation_id)
    if not authors_ids:
        yield []

    author_ccs = db.person.find(
        {
            "_id": {"$in": list(authors_ids)},
            "external_ids.source": {"$in": ["Cédula de Ciudadanía", "Cédula de Extranjería", "Pasaporte", "Passport"]},
        },
        {"external_ids.$": 1},
    )
    authors_ccs = {doc["external_ids"][0]["id"] for doc in author_ccs if doc.get("external_ids")}

    if not authors_ccs:
        yield []

    pipeline = [
        {"$match": {"professor_id": {"$in": list(authors_ccs)}}},
        {"$project": {"classified_urls_ids": 1}},
        {"$unwind": "$classified_urls_ids"},
        {
            "$lookup": {
                "from": "news_urls_collection",
                "localField": "classified_urls_ids",
                "foreignField": "url_id",
                "as": "url_docs",
            }
        },
        {"$unwind": "$url_docs"},
        {
            "$lookup": {
                "from": "news_media_collection",
                "localField": "url_docs.medium_id",
                "foreignField": "medium_id",
                "as": "medium_docs",
            }
        },
        {"$unwind": "$medium_docs"},
        {"$replaceRoot": {"newRoot": {"$mergeObjects": ["$url_docs", {"medium": "$medium_docs.medium"}]}}},
    ]
    if sort := query_params.sort:
        if sort == "alphabetical_asc":
            pipeline.append({"$sort": {"url_title": 1}})
        if sort == "year_desc":
            pipeline.append({"$sort": {"url_date": -1}})
    base_repository.set_pagination(pipeline, query_params)
    cursor = db.news_professors_collection.aggregate(pipeline, allowDiskUse=True)
    yield from news_generator.get(cursor)


def news_count_by_affiliation(affiliation_id: str, affiliation_type: str) -> int:
    """
    Counts the number of news entries associated with a given affiliation.

    Executes an aggregation pipeline to compute the total number of news
    records linked to authors associated with the affiliation.

    Parameters:
    -----------
    affiliation_id : str
        The ID of the affiliation whose news entries are to be counted.
    affiliation_type : str
        The type of the affiliation (e.g., "institution", "department").

    Returns:
    --------
    int
        Total number of matching news entries.
    """
    authors_ids = author_ids_for_affiliation(db, affiliation_id)
    if not authors_ids:
        return 0
    author_ccs = db.person.find(
        {
            "_id": {"$in": list(authors_ids)},
            "external_ids.source": {"$in": ["Cédula de Ciudadanía", "Cédula de Extranjería", "Pasaporte", "Passport"]},
        },
        {"external_ids.$": 1},
    )
    authors_ccs = {doc["external_ids"][0]["id"] for doc in author_ccs if doc.get("external_ids")}
    if not authors_ccs:
        return 0

    pipeline = [
        {"$match": {"professor_id": {"$in": list(authors_ccs)}}},
        {"$project": {"classified_urls_ids": 1}},
        {"$unwind": "$classified_urls_ids"},
        {
            "$lookup": {
                "from": "news_urls_collection",
                "localField": "classified_urls_ids",
                "foreignField": "url_id",
                "as": "url_docs",
            }
        },
        {"$unwind": "$url_docs"},
        {
            "$lookup": {
                "from": "news_media_collection",
                "localField": "url_docs.medium_id",
                "foreignField": "medium_id",
                "as": "medium_docs",
            }
        },
        {"$unwind": "$medium_docs"},
        {"$count": "total"},
    ]
    result = list(db.news_professors_collection.aggregate(pipeline))
    return int(result[0]["total"]) if result else 0
