from infrastructure.mongo import database


def set_affiliations_hash():  # type: ignore
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


def set_works_authors_affiliations_hash():  # type: ignore
    pipeline = [
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "authors.affiliations.id",
                "foreignField": "_id",
                "as": "affiliations_data",
                "pipeline": [{"$project": {"_id": 1, "hash": 1}}],
            }
        },
        {
            "$addFields": {
                "authors": {
                    "$map": {
                        "input": "$authors",
                        "as": "author",
                        "in": {
                            "$mergeObjects": [
                                "$$author",
                                {
                                    "affiliations": {
                                        "$map": {
                                            "input": "$$author.affiliations",
                                            "as": "affiliation",
                                            "in": {
                                                "$mergeObjects": [
                                                    "$$affiliation",
                                                    {
                                                        "hash": {
                                                            "$let": {
                                                                "vars": {
                                                                    "matchedAffiliation": {
                                                                        "$arrayElemAt": [
                                                                            {
                                                                                "$filter": {
                                                                                    "input": "$affiliations_data",
                                                                                    "as": "affiliation_data",
                                                                                    "cond": {
                                                                                        "$eq": [
                                                                                            "$$affiliation.id",
                                                                                            "$$affiliation_data._id",
                                                                                        ]
                                                                                    },
                                                                                }
                                                                            },
                                                                            0,
                                                                        ]
                                                                    }
                                                                },
                                                                "in": "$$matchedAffiliation.hash",
                                                            }
                                                        }
                                                    },
                                                ]
                                            },
                                        }
                                    }
                                },
                            ]
                        },
                    }
                }
            }
        },
        {"$project": {"affiliations_data": 0}},
        {
            "$merge": {
                "into": "works",
                "whenMatched": "merge",
                "whenNotMatched": "fail",
            }
        },
    ]
    database["works"].aggregate(pipeline)


def set_person_affiliations_hash():  # type: ignore
    pipeline = [
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "affiliations.id",
                "foreignField": "_id",
                "as": "affiliations_data",
                "pipeline": [{"$project": {"_id": 1, "hash": 1}}],
            }
        },
        {
            "$addFields": {
                "affiliations": {
                    "$map": {
                        "input": "$affiliations",
                        "as": "affiliation",
                        "in": {
                            "$mergeObjects": [
                                "$$affiliation",
                                {
                                    "hash": {
                                        "$let": {
                                            "vars": {
                                                "matchedAffiliation": {
                                                    "$arrayElemAt": [
                                                        {
                                                            "$filter": {
                                                                "input": "$affiliations_data",
                                                                "as": "affiliation_data",
                                                                "cond": {
                                                                    "$eq": [
                                                                        "$$affiliation.id",
                                                                        "$$affiliation_data._id",
                                                                    ]
                                                                },
                                                            }
                                                        },
                                                        0,
                                                    ]
                                                }
                                            },
                                            "in": "$$matchedAffiliation.hash",
                                        }
                                    }
                                },
                            ]
                        },
                    }
                }
            }
        },
        {"$project": {"affiliations_data": 0}},
        {
            "$merge": {
                "into": "person",
                "whenMatched": "merge",
                "whenNotMatched": "fail",
            }
        },
    ]
    database["person"].aggregate(pipeline)


def set_affiliation_relations_hash():  # type: ignore
    pipeline = [
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "relations.id",
                "foreignField": "_id",
                "as": "relations_data",
                "pipeline": [{"$project": {"_id": 1, "hash": 1}}],
            }
        },
        {
            "$addFields": {
                "relations": {
                    "$map": {
                        "input": "$relations",
                        "as": "relation",
                        "in": {
                            "$mergeObjects": [
                                "$$relation",
                                {
                                    "hash": {
                                        "$let": {
                                            "vars": {
                                                "matchedRelation": {
                                                    "$arrayElemAt": [
                                                        {
                                                            "$filter": {
                                                                "input": "$relations_data",
                                                                "as": "relation_data",
                                                                "cond": {
                                                                    "$eq": [
                                                                        "$$relation.id",
                                                                        "$$relation_data._id",
                                                                    ]
                                                                },
                                                            }
                                                        },
                                                        0,
                                                    ]
                                                }
                                            },
                                            "in": "$$matchedRelation.hash",
                                        }
                                    }
                                },
                            ]
                        },
                    }
                }
            }
        },
        {"$project": {"relations_data": 0}},
        {
            "$merge": {
                "into": "affiliations",
                "whenMatched": "merge",
                "whenNotMatched": "fail",
            }
        },
    ]
    database["affiliations"].aggregate(pipeline)
