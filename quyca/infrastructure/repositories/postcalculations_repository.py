from typing import Any, Dict, List
from quyca.infrastructure.mongo import database


def set_works_authors_affiliations_country() -> None:
    pipeline: List[Dict[str, Any]] = [
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "authors.affiliations.id",
                "foreignField": "_id",
                "as": "affiliations_data",
                "pipeline": [{"$project": {"_id": 1, "addresses.country": 1}}],
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
                                                        "country": {
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
                                                                "in": {
                                                                    "$ifNull": [
                                                                        {
                                                                            "$arrayElemAt": [
                                                                                "$$matchedAffiliation.addresses.country",
                                                                                0,
                                                                            ]
                                                                        },
                                                                        None,
                                                                    ]
                                                                },
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


def set_works_authors_affiliations_country_code() -> None:
    pipeline: List[Dict[str, Any]] = [
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "authors.affiliations.id",
                "foreignField": "_id",
                "as": "affiliations_data",
                "pipeline": [{"$project": {"_id": 1, "addresses.country_code": 1}}],
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
                                                        "country_code": {
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
                                                                "in": {
                                                                    "$ifNull": [
                                                                        {
                                                                            "$arrayElemAt": [
                                                                                "$$matchedAffiliation.addresses.country_code",
                                                                                0,
                                                                            ]
                                                                        },
                                                                        None,
                                                                    ]
                                                                },
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


def set_works_groups_ranking() -> None:
    pipeline: List[Dict[str, Any]] = [
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "groups.id",
                "foreignField": "_id",
                "as": "groups_data",
                "pipeline": [{"$match": {"ranking.source": "minciencias"}}, {"$project": {"_id": 1, "ranking": 1}}],
            }
        },
        {
            "$addFields": {
                "groups": {
                    "$map": {
                        "input": "$groups",
                        "as": "group",
                        "in": {
                            "$mergeObjects": [
                                "$$group",
                                {
                                    "ranking": {
                                        "$let": {
                                            "vars": {
                                                "matchedGroup": {
                                                    "$arrayElemAt": [
                                                        {
                                                            "$filter": {
                                                                "input": "$groups_data",
                                                                "as": "group_data",
                                                                "cond": {
                                                                    "$eq": [
                                                                        "$$group.id",
                                                                        "$$group_data._id",
                                                                    ]
                                                                },
                                                            }
                                                        },
                                                        0,
                                                    ]
                                                }
                                            },
                                            "in": {
                                                "$ifNull": [
                                                    {
                                                        "$arrayElemAt": [
                                                            {
                                                                "$map": {
                                                                    "input": {
                                                                        "$filter": {
                                                                            "input": "$$matchedGroup.ranking",
                                                                            "as": "rankData",
                                                                            "cond": {
                                                                                "$eq": [
                                                                                    "$$rankData.source",
                                                                                    "minciencias",
                                                                                ]
                                                                            },
                                                                        }
                                                                    },
                                                                    "as": "filteredRank",
                                                                    "in": "$$filteredRank.rank",
                                                                }
                                                            },
                                                            0,
                                                        ]
                                                    },
                                                    None,
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
        {"$project": {"groups_data": 0}},
        {
            "$merge": {
                "into": "works",
                "whenMatched": "merge",
                "whenNotMatched": "fail",
            }
        },
    ]
    database["works"].aggregate(pipeline)


def set_works_authors_ranking() -> None:
    pipeline: List[Dict[str, Any]] = [
        {
            "$lookup": {
                "from": "person",
                "localField": "authors.id",
                "foreignField": "_id",
                "as": "authors_data",
                "pipeline": [{"$match": {"ranking.source": "minciencias"}}, {"$project": {"_id": 1, "ranking": 1}}],
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
                                    "ranking": {
                                        "$let": {
                                            "vars": {
                                                "matchedAuthor": {
                                                    "$arrayElemAt": [
                                                        {
                                                            "$filter": {
                                                                "input": "$authors_data",
                                                                "as": "author_data",
                                                                "cond": {
                                                                    "$eq": [
                                                                        "$$author.id",
                                                                        "$$author_data._id",
                                                                    ]
                                                                },
                                                            }
                                                        },
                                                        0,
                                                    ]
                                                }
                                            },
                                            "in": {
                                                "$ifNull": [
                                                    {
                                                        "$arrayElemAt": [
                                                            {
                                                                "$map": {
                                                                    "input": {
                                                                        "$filter": {
                                                                            "input": "$$matchedAuthor.ranking",
                                                                            "as": "rankData",
                                                                            "cond": {
                                                                                "$eq": [
                                                                                    "$$rankData.source",
                                                                                    "minciencias",
                                                                                ]
                                                                            },
                                                                        }
                                                                    },
                                                                    "as": "filteredRank",
                                                                    "in": "$$filteredRank.rank",
                                                                }
                                                            },
                                                            0,
                                                        ]
                                                    },
                                                    None,
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
        {"$project": {"authors_data": 0}},
        {
            "$merge": {
                "into": "works",
                "whenMatched": "merge",
                "whenNotMatched": "fail",
            }
        },
    ]
    database["works"].aggregate(pipeline)
