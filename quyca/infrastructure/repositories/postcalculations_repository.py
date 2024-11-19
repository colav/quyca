from infrastructure.mongo import database


def set_affiliations_hash(): # type: ignore
    pipeline = [
        {
            "$addFields": {
                "ror_id": {
                    "$ifNull": [
                        {
                            "$arrayElemAt": [
                                {
                                    "$map": {
                                        "input": {
                                            "$filter": {
                                                "input": "$external_ids",
                                                "as": "external_id",
                                                "cond": {"$eq": ["$$external_id.source", "ror"]},
                                            }
                                        },
                                        "as": "filtered",
                                        "in": "$$filtered.id",
                                    }
                                },
                                0,
                            ]
                        },
                        None,
                    ]
                }
            }
        },
        {
            "$addFields": {
                "hash": {
                    "$cond": {
                        "if": {"$ne": ["$ror_id", None]},
                        "then": {"$substr": ["$ror_id", {"$subtract": [{"$strLenCP": "$ror_id"}, 9]}, 9]},
                        "else": {"$toString": "$_id"},
                    }
                }
            }
        },
        {"$project": {"ror_id": 0}},
        {
            "$merge": {
                "into": "affiliations",
                "whenMatched": "merge",
                "whenNotMatched": "fail",
            }
        },
    ]
    database["affiliations"].aggregate(pipeline)
