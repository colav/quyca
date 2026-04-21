from quyca.domain.constants.institutions import institutions_list
from quyca.infrastructure.mongo import database


def get_last_db_update() -> int:
    doc = database["log"].find_one(sort=[("time", -1)], projection={"time": 1})

    if doc:
        return int(doc["time"])

    return 0


def get_entity_count(entity: str, affiliation_type: str | None = None) -> int:
    if affiliation_type:
        if affiliation_type == "institution":
            return database[entity].count_documents({"types.type": {"$in": institutions_list}})
        return database[entity].count_documents({"types.type": affiliation_type})
    return database[entity].estimated_document_count()


def get_open_access_count() -> int:
    return database["works"].count_documents({"open_access.is_open_access": True})


def get_news_count() -> int:
    return database["news_urls_collection"].estimated_document_count()
