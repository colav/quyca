from quyca.domain.constants.institutions import institutions_list
from quyca.infrastructure.mongo import database
from typing import Any

_works_quality_cache: dict | None = None
_person_quality_cache: dict | None = None


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


def get_works_quality_metrics() -> dict:
    global _works_quality_cache
    if _works_quality_cache is not None:
        return _works_quality_cache
    _works_quality_cache = _compute_works_quality_metrics()
    return _works_quality_cache


def invalidate_works_quality_cache() -> None:
    global _works_quality_cache
    _works_quality_cache = None


def _compute_works_quality_metrics() -> dict:
    ALL_SOURCES = ["ciarp", "dspace", "minciencias", "openalex", "scholar", "scienti"]
    MAIN_SOURCES = ["scienti", "minciencias", "openalex"]
    pipeline = [
        {
            "$facet": {
                "with_doi": [{"$match": {"doi": {"$nin": [None, ""]}}}, {"$count": "n"}],
                "with_abstract": [{"$match": {"abstracts.0": {"$exists": True}}}, {"$count": "n"}],
                "with_primary_topic": [{"$match": {"primary_topic": {"$nin": [None, {}]}}}, {"$count": "n"}],
                "with_year_published": [{"$match": {"year_published": {"$ne": None}}}, {"$count": "n"}],
                "with_source": [{"$match": {"source.id": {"$nin": [None, ""]}}}, {"$count": "n"}],
                "open_access_status_known": [
                    {"$match": {"open_access.is_open_access": {"$ne": None}}},
                    {"$count": "n"},
                ],
                "with_apc_paid": [{"$match": {"apc.paid.value": {"$ne": None}}}, {"$count": "n"}],
                "with_citations": [{"$match": {"citations_count_openalex": {"$gt": 0}}}, {"$count": "n"}],
                "with_ranking_minciencias": [
                    {"$match": {"ranking": {"$elemMatch": {"source": "minciencias"}}}},
                    {"$count": "n"},
                ],
                "with_research_groups": [{"$match": {"groups.0": {"$exists": True}}}, {"$count": "n"}],
                "provenance_breakdown": [
                    {"$project": {"combo": {"$setIntersection": [{"$ifNull": ["$updated.source", []]}, ALL_SOURCES]}}},
                    {"$group": {"_id": "$combo", "count": {"$sum": 1}}},
                ],
                "impactu_types": [
                    {"$unwind": "$types"},
                    {"$match": {"types.source": "impactu"}},
                    {"$group": {"_id": "$types.type", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ],
                "without_impactu_no_types": [
                    {"$match": {"$or": [{"types": {"$exists": False}}, {"types": []}]}},
                    {"$count": "n"},
                ],
                "without_impactu_normalization_skipped": [
                    {
                        "$match": {
                            "$and": [
                                {"types": {"$not": {"$elemMatch": {"source": "impactu"}}}},
                                {
                                    "$expr": {
                                        "$gt": [
                                            {
                                                "$size": {
                                                    "$filter": {
                                                        "input": {"$ifNull": ["$types", []]},
                                                        "as": "t",
                                                        "cond": {"$in": ["$$t.source", MAIN_SOURCES]},
                                                    }
                                                }
                                            },
                                            0,
                                        ]
                                    }
                                },
                            ]
                        }
                    },
                    {"$count": "n"},
                ],
                "without_impactu_by_source": [
                    {
                        "$match": {
                            "$and": [
                                {"types": {"$not": {"$elemMatch": {"source": "impactu"}}}},
                                {"types.0": {"$exists": True}},
                            ]
                        }
                    },
                    {
                        "$project": {
                            "sources": {"$setUnion": [{"$map": {"input": "$types", "as": "t", "in": "$$t.source"}}, []]}
                        }
                    },
                    {"$unwind": "$sources"},
                    {"$group": {"_id": "$sources", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ],
            }
        }
    ]

    result: dict[str, Any] = next(database["works"].aggregate(pipeline, allowDiskUse=True), {})

    non_scalar = (
        "provenance_breakdown",
        "impactu_types",
        "without_impactu_no_types",
        "without_impactu_normalization_skipped",
        "without_impactu_by_source",
    )
    metrics: dict[str, Any] = {
        key: (result[key][0]["n"] if result.get(key) else 0) for key in result if key not in non_scalar
    }

    totals_provenance: dict[str, int] = {}
    for item in result.get("provenance_breakdown", []):
        for source in item["_id"]:
            totals_provenance[source] = totals_provenance.get(source, 0) + item["count"]

    metrics["provenance_breakdown"] = {
        ("_".join(sorted(item["_id"])) if item["_id"] else "none"): item["count"]
        for item in result.get("provenance_breakdown", [])
    }
    metrics["provenance_breakdown"]["totals_provenance"] = dict(
        sorted(totals_provenance.items(), key=lambda x: x[1], reverse=True)
    )

    assigned = sum(item["count"] for item in result.get("impactu_types", []))
    metrics["total"] = database["works"].estimated_document_count()
    metrics["types_breakdown"] = {
        "with_impactu_total": assigned,
        "without_impactu_total": metrics["total"] - assigned,
        "impactu": [{"type": item["_id"], "count": item["count"]} for item in result.get("impactu_types", [])],
        "without_impactu": {
            "no_types": result.get("without_impactu_no_types", [{}])[0].get("n", 0),
            "normalization_skipped": result.get("without_impactu_normalization_skipped", [{}])[0].get("n", 0),
            "by_source": {item["_id"]: item["count"] for item in result.get("without_impactu_by_source", [])},
        },
    }
    return metrics


def get_person_quality_metrics() -> dict:
    global _person_quality_cache
    if _person_quality_cache is not None:
        return _person_quality_cache
    _person_quality_cache = _compute_person_quality_metrics()
    return _person_quality_cache


def invalidate_person_quality_cache() -> None:
    global _person_quality_cache
    _person_quality_cache = None


def _compute_person_quality_metrics() -> dict:
    ALL_SOURCES = ["minciencias", "openalex", "orcid", "scholar", "scienti", "staff"]
    pipeline = [
        {
            "$facet": {
                "with_citations": [{"$match": {"citations_count_openalex": {"$gt": 0}}}, {"$count": "n"}],
                "with_hindex": [{"$match": {"h_index": {"$gt": 0}}}, {"$count": "n"}],
                "with_cedula_scienti": [
                    {
                        "$match": {
                            "external_ids": {
                                "$elemMatch": {
                                    "source": {"$in": ["Cédula de Ciudadanía", "Cédula de Extranjería", "Passport"]},
                                    "provenance": "scienti",
                                }
                            }
                        }
                    },
                    {"$count": "n"},
                ],
                "with_cedula_staff": [
                    {
                        "$match": {
                            "external_ids": {
                                "$elemMatch": {
                                    "source": {"$in": ["Cédula de Ciudadanía", "Cédula de Extranjería", "Passport"]},
                                    "provenance": "staff",
                                }
                            }
                        }
                    },
                    {"$count": "n"},
                ],
                "provenance_breakdown": [
                    {"$project": {"combo": {"$setIntersection": [{"$ifNull": ["$updated.source", []]}, ALL_SOURCES]}}},
                    {"$group": {"_id": "$combo", "count": {"$sum": 1}}},
                ],
                "external_ids_breakdown": [
                    {
                        "$project": {
                            "sources": {
                                "$setUnion": [
                                    {
                                        "$map": {
                                            "input": {"$ifNull": ["$external_ids", []]},
                                            "as": "e",
                                            "in": "$$e.source",
                                        }
                                    },
                                    [],
                                ]
                            }
                        }
                    },
                    {"$unwind": "$sources"},
                    {"$group": {"_id": "$sources", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ],
            }
        }
    ]

    result: dict[str, Any] = next(database["person"].aggregate(pipeline, allowDiskUse=True), {})

    non_scalar = ("provenance_breakdown", "external_ids_breakdown", "with_cedula_scienti", "with_cedula_staff")
    metrics: dict[str, Any] = {
        key: (result[key][0]["n"] if result.get(key) else 0) for key in result if key not in non_scalar
    }

    totals_provenance: dict[str, int] = {}
    for item in result.get("provenance_breakdown", []):
        for source in item["_id"]:
            totals_provenance[source] = totals_provenance.get(source, 0) + item["count"]

    metrics["provenance_breakdown"] = {
        ("_".join(sorted(item["_id"])) if item["_id"] else "none"): item["count"]
        for item in result.get("provenance_breakdown", [])
    }
    metrics["provenance_breakdown"]["totals_provenance"] = dict(
        sorted(totals_provenance.items(), key=lambda x: x[1], reverse=True)
    )

    metrics["external_ids_breakdown"] = {
        item["_id"]: item["count"] for item in result.get("external_ids_breakdown", [])
    }

    cedula_scienti = result.get("with_cedula_scienti", [{}])[0].get("n", 0)
    cedula_staff = result.get("with_cedula_staff", [{}])[0].get("n", 0)
    metrics["with_cedula"] = {
        "total": cedula_scienti + cedula_staff,
        "scienti": cedula_scienti,
        "staff": cedula_staff,
    }

    # Derivados desde datos ya calculados — sin ramas extra en $facet
    metrics["with_orcid"] = metrics["external_ids_breakdown"].get("orcid", 0)
    metrics["with_staff"] = metrics["provenance_breakdown"]["totals_provenance"].get("staff", 0)
    metrics["total"] = database["person"].estimated_document_count()
    return metrics


_affiliations_quality_cache: dict | None = None


def get_affiliations_quality_metrics() -> dict:
    global _affiliations_quality_cache
    if _affiliations_quality_cache is not None:
        return _affiliations_quality_cache
    _affiliations_quality_cache = _compute_affiliations_quality_metrics()
    return _affiliations_quality_cache


def invalidate_affiliations_quality_cache() -> None:
    global _affiliations_quality_cache
    _affiliations_quality_cache = None


def _compute_affiliations_quality_metrics() -> dict:
    ALL_SOURCES = ["minciencias", "openalex", "ror", "scienti", "staff", "wikidata"]
    pipeline = [
        {
            "$facet": {
                "with_country": [{"$match": {"addresses.0": {"$exists": True}}}, {"$count": "n"}],
                "with_year_established": [{"$match": {"year_established": {"$ne": None}}}, {"$count": "n"}],
                "with_products": [{"$match": {"products_count": {"$gt": 0}}}, {"$count": "n"}],
                "with_citations": [{"$match": {"citations_count_openalex": {"$gt": 0}}}, {"$count": "n"}],
                "with_hindex": [{"$match": {"h_index": {"$gt": 0}}}, {"$count": "n"}],
                "with_relations": [{"$match": {"relations.0": {"$exists": True}}}, {"$count": "n"}],
                "colombian": [{"$match": {"addresses": {"$elemMatch": {"country_code": "CO"}}}}, {"$count": "n"}],
                "research_groups": [
                    # If ranking.0 exists, it has a Minciencias/Scienti classification — it's always of type group.
                    {"$match": {"ranking.0": {"$exists": True}}},
                    {"$count": "n"},
                ],
                "provenance_breakdown": [
                    {"$project": {"combo": {"$setIntersection": [{"$ifNull": ["$updated.source", []]}, ALL_SOURCES]}}},
                    {"$group": {"_id": "$combo", "count": {"$sum": 1}}},
                ],
                "types_breakdown": [
                    {"$unwind": "$types"},
                    {
                        "$match": {
                            "types.source": {"$in": ["ror", "staff", "minciencias", "scienti"]},
                            "types.type": {"$nin": ["Funder", "funder"]},
                        }
                    },
                    {"$group": {"_id": {"$toLower": "$types.type"}, "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ],
                "external_ids_breakdown": [
                    {
                        "$project": {
                            "sources": {
                                "$setUnion": [
                                    {
                                        "$map": {
                                            "input": {"$ifNull": ["$external_ids", []]},
                                            "as": "e",
                                            "in": "$$e.source",
                                        }
                                    },
                                    [],
                                ]
                            }
                        }
                    },
                    {"$unwind": "$sources"},
                    {"$group": {"_id": "$sources", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ],
            }
        }
    ]

    result: dict[str, Any] = next(database["affiliations"].aggregate(pipeline, allowDiskUse=True), {})

    non_scalar = ("provenance_breakdown", "types_breakdown", "external_ids_breakdown")
    metrics: dict[str, Any] = {
        key: (result[key][0]["n"] if result.get(key) else 0) for key in result if key not in non_scalar
    }

    totals_provenance: dict[str, int] = {}
    for item in result.get("provenance_breakdown", []):
        for source in item["_id"]:
            totals_provenance[source] = totals_provenance.get(source, 0) + item["count"]

    metrics["provenance_breakdown"] = {
        ("_".join(sorted(item["_id"])) if item["_id"] else "none"): item["count"]
        for item in result.get("provenance_breakdown", [])
    }
    metrics["provenance_breakdown"]["totals_provenance"] = dict(
        sorted(totals_provenance.items(), key=lambda x: x[1], reverse=True)
    )
    metrics["types_breakdown"] = {item["_id"]: item["count"] for item in result.get("types_breakdown", [])}
    metrics["external_ids_breakdown"] = {
        item["_id"]: item["count"] for item in result.get("external_ids_breakdown", [])
    }
    metrics["total"] = database["affiliations"].estimated_document_count()
    return metrics


_sources_quality_cache: dict | None = None


def get_sources_quality_metrics() -> dict:
    global _sources_quality_cache
    if _sources_quality_cache is not None:
        return _sources_quality_cache
    _sources_quality_cache = _compute_sources_quality_metrics()
    return _sources_quality_cache


def invalidate_sources_quality_cache() -> None:
    global _sources_quality_cache
    _sources_quality_cache = None


def _compute_sources_quality_metrics() -> dict:
    ALL_SOURCES = ["doaj", "openalex", "scienti", "scimago"]
    pipeline = [
        {
            "$facet": {
                "with_publisher": [{"$match": {"publisher.name": {"$nin": [None, ""]}}}, {"$count": "n"}],
                "with_apc": [{"$match": {"apc": {"$ne": {}}, "apc.charges": {"$gt": 0}}}, {"$count": "n"}],
                "with_ranking": [{"$match": {"ranking.0": {"$exists": True}}}, {"$count": "n"}],
                "with_products": [{"$match": {"products_count": {"$gt": 0}}}, {"$count": "n"}],
                "with_topics": [{"$match": {"topics.0": {"$exists": True}}}, {"$count": "n"}],
                "with_licenses": [{"$match": {"licenses.0": {"$exists": True}}}, {"$count": "n"}],
                "open_access_breakdown": [
                    {"$match": {"open_access_status": {"$ne": None}}},
                    {"$group": {"_id": "$open_access_status", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ],
                "scimago_quartiles_breakdown": [
                    {"$match": {"scimago_best_quartile": {"$nin": [None, ""]}}},
                    {"$group": {"_id": "$scimago_best_quartile", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ],
                "source_types_breakdown": [
                    {"$unwind": "$types"},
                    {"$match": {"types.source": "openalex"}},
                    {"$group": {"_id": "$types.type", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ],
                "license_type_breakdown": [
                    {"$unwind": "$licenses"},
                    {"$group": {"_id": "$licenses.type", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ],
                "provenance_breakdown": [
                    {"$project": {"combo": {"$setIntersection": [{"$ifNull": ["$updated.source", []]}, ALL_SOURCES]}}},
                    {"$group": {"_id": "$combo", "count": {"$sum": 1}}},
                ],
                "external_ids_breakdown": [
                    {
                        "$project": {
                            "sources": {
                                "$setUnion": [
                                    {
                                        "$map": {
                                            "input": {"$ifNull": ["$external_ids", []]},
                                            "as": "e",
                                            "in": "$$e.source",
                                        }
                                    },
                                    [],
                                ]
                            }
                        }
                    },
                    {"$unwind": "$sources"},
                    {"$group": {"_id": "$sources", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ],
            }
        }
    ]

    result: dict[str, Any] = next(database["sources"].aggregate(pipeline, allowDiskUse=True), {})

    non_scalar = (
        "open_access_breakdown",
        "scimago_quartiles_breakdown",
        "source_types_breakdown",
        "license_type_breakdown",
        "provenance_breakdown",
        "external_ids_breakdown",
    )
    metrics: dict[str, Any] = {
        key: (result[key][0]["n"] if result.get(key) else 0) for key in result if key not in non_scalar
    }

    totals_provenance: dict[str, int] = {}
    for item in result.get("provenance_breakdown", []):
        for source in item["_id"]:
            totals_provenance[source] = totals_provenance.get(source, 0) + item["count"]

    metrics["provenance_breakdown"] = {
        ("_".join(sorted(item["_id"])) if item["_id"] else "none"): item["count"]
        for item in result.get("provenance_breakdown", [])
    }
    metrics["provenance_breakdown"]["totals_provenance"] = dict(
        sorted(totals_provenance.items(), key=lambda x: x[1], reverse=True)
    )
    metrics["open_access_breakdown"] = {item["_id"]: item["count"] for item in result.get("open_access_breakdown", [])}
    metrics["scimago_quartiles_breakdown"] = {
        item["_id"]: item["count"] for item in result.get("scimago_quartiles_breakdown", [])
    }
    metrics["source_types_breakdown"] = {
        item["_id"]: item["count"] for item in result.get("source_types_breakdown", [])
    }
    metrics["license_type_breakdown"] = {
        item["_id"]: item["count"] for item in result.get("license_type_breakdown", [])
    }
    metrics["external_ids_breakdown"] = {
        item["_id"]: item["count"] for item in result.get("external_ids_breakdown", [])
    }
    metrics["total"] = database["sources"].estimated_document_count()
    return metrics
