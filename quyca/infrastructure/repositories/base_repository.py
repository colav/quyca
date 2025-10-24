from quyca.domain.models.base_model import QueryParams


def set_search_end_stages(pipeline: list, query_params: QueryParams, pipeline_params: dict | None = None) -> list:
    if pipeline_params is None:
        pipeline_params = {}
    set_sort(query_params.sort, pipeline, pipeline_params.get("collection"))
    set_project(pipeline, pipeline_params.get("project"))
    set_pagination(pipeline, query_params)
    return pipeline


def set_pagination(pipeline: list, query_params: QueryParams) -> None:
    if (page := query_params.page) and (limit := query_params.limit):
        skip = (page - 1) * limit
        pipeline += [{"$skip": skip}, {"$limit": limit}]


def set_match(pipeline: list, match: dict | None) -> None:
    if not match:
        return
    pipeline += [{"$match": match}]


def set_project(pipeline: list, project: list | dict | None) -> None:
    if not project:
        return

    pipeline.append({"$project": {"_id": 1, **{p: 1 for p in project}}})


def set_sort(sort: str | None, pipeline: list, collection: str | None = None) -> None:
    if not sort:
        return
    sort_field, direction_str = sort.split("_")
    direction = -1 if direction_str == "desc" else 1

    if sort_field == "citations":
        if collection == "sources":
            pipeline += [
                {
                    "$addFields": {
                        "citations_count_openalex": {
                            "$let": {
                                "vars": {
                                    "openalexCitation": {
                                        "$arrayElemAt": [
                                            {
                                                "$filter": {
                                                    "input": "$citations_count",
                                                    "as": "cite",
                                                    "cond": {"$eq": ["$$cite.source", "openalex"]}
                                                }
                                            },
                                            0
                                        ]
                                    }
                                },
                                "in": {
                                    "$ifNull": ["$$openalexCitation.count", 0]
                                }
                            }
                        }
                    }
                }
            ]
            sort_field = "citations_count_openalex"
        else:
            sort_field = "citations_count_openalex"
    elif sort_field == "alphabetical":
        if collection == "sources":
            pipeline += [
                {
                    "$addFields": {
                        "names_order": {
                            "$map": {
                                "input": "$names",
                                "as": "name",
                                "in": {
                                    "source": "$$name.source",
                                    "name": "$$name.name",
                                    "order": {
                                        "$switch": {
                                            "branches": [
                                                {
                                                    "case": {
                                                        "$eq": [
                                                            "$$name.source",
                                                            "openalex",
                                                        ]
                                                    },
                                                    "then": 0,
                                                },
                                                {
                                                    "case": {"$eq": ["$$name.source", "doaj"]},
                                                    "then": 1,
                                                },
                                                {
                                                    "case": {"$eq": ["$$name.source", "scimago"]},
                                                    "then": 2,
                                                },
                                                {
                                                    "case": {"$eq": ["$$name.source", "scholar"]},
                                                    "then": 3,
                                                },
                                            ],
                                            "default": 10,
                                        }
                                    },
                                },
                            }
                        }
                    }
                },
                {
                    "$addFields": {
                        "first_name": {
                            "$arrayElemAt": [
                                {
                                    "$sortArray": {
                                        "input": "$names_order",
                                        "sortBy": {"order": 1},
                                    }
                                },
                                0,
                            ]
                        }
                    }
                },
                {"$addFields": {"sort_name": "$first_name.name"}},
                {"$unset": ["names_order", "first_name"]},
            ]
            sort_field = "sort_name"
        else: 
            pipeline += [
                {
                    "$addFields": {
                        "titles_order": {
                            "$map": {
                                "input": "$titles",
                                "as": "title",
                                "in": {
                                    "source": "$$title.source",
                                    "title": "$$title.title",
                                    "order": {
                                        "$switch": {
                                            "branches": [
                                                {
                                                    "case": {
                                                        "$eq": [
                                                            "$$title.source",
                                                            "openalex",
                                                        ]
                                                    },
                                                    "then": 0,
                                                },
                                                {
                                                    "case": {"$eq": ["$$title.source", "scholar"]},
                                                    "then": 1,
                                                },
                                                {
                                                    "case": {"$eq": ["$$title.source", "scienti"]},
                                                    "then": 2,
                                                },
                                                {
                                                    "case": {
                                                        "$eq": [
                                                            "$$title.source",
                                                            "minciencias",
                                                        ]
                                                    },
                                                    "then": 3,
                                                },
                                                {
                                                    "case": {"$eq": ["$$title.source", "ranking"]},
                                                    "then": 4,
                                                },
                                                {
                                                    "case": {"$eq": ["$$title.source", "siiu"]},
                                                    "then": 5,
                                                },
                                            ],
                                            "default": 10,
                                        }
                                    },
                                },
                            }
                        }
                    }
                },
                {
                    "$addFields": {
                        "first_title": {
                            "$arrayElemAt": [
                                {
                                    "$sortArray": {
                                        "input": "$titles_order",
                                        "sortBy": {"order": 1},
                                    }
                                },
                                0,
                            ]
                        }
                    }
                },
                {"$addFields": {"title": "$first_title.title"}},
                {"$unset": ["titles_order", "first_title"]},
            ]
            sort_field = "title"
    elif sort_field == "products":
        sort_field = "products_count"
    elif sort_field == "year":
        pipeline += [
            {
                "$addFields": {
                    "sort_year": {
                        "$cond": {
                            "if": {
                                "$or": [
                                    {"$eq": ["$year_published", None]},
                                    {"$eq": ["$year_published", ""]},
                                ]
                            },
                            "then": -1,
                            "else": "$year_published",
                        }
                    }
                }
            },
        ]
        sort_field = "sort_year"
    pipeline += [{"$sort": {sort_field: direction, "_id": 1}}]
