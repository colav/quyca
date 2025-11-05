from typing import List

from quyca.domain.constants.source_types import (
    NORMALIZED_TYPE_MAPPING,
    QUARTILE_MAPPING,
    SOURCE_TITLES,
    TYPE_DISPLAY_MAPPING,
)
from quyca.domain.models.source_model import Source


def parse_source(source: Source) -> dict:
    include = [
        "id",
        "updated",
        "names",
        "abbreviations",
        "types",
        "keywords",
        "languages",
        "publisher",
        "relations",
        "addresses",
        "external_ids",
        "external_urls",
        "waiver",
        "plagiarism_detection",
        "open_access_start_year",
        "publication_time_weeks",
        "products_count",
        "citations_count",
        "apc",
        "copyright",
        "licenses",
        "subjects",
        "ranking",
        "review_process",
    ]
    return source.model_dump(include=include, exclude_none=True)


def parse_search_result(sources: List) -> List:
    """
    This function use model dumping to extract relevant fields from source entities.

    Parameters:
    -----------
    sources : List
        A list of source entities to be parsed.

    Returns:
    --------
    List
        A list of dictionaries containing the relevant fields from each source entity.
    """
    source_fields = [
        "id",
        "updated",
        "names",
        "abbreviations",
        "types",
        "keywords",
        "languages",
        "publisher",
        "relations",
        "addresses",
        "external_ids",
        "external_urls",
        "waiver",
        "plagiarism_detection",
        "open_access_start_year",
        "publication_time_weeks",
        "products_count",
        "citations_count",
        "apc",
        "copyright",
        "licenses",
        "subjects",
        "ranking",
        "review_process",
    ]

    return [
        source.model_dump(include=source_fields, exclude={"citations_count": {"__all__": {"provenance"}}})
        for source in sources
    ]


def parse_available_filters(filters: dict) -> dict:
    """
    Parses the available filters from the search results.

    Parameters:
    -----------
    filters : dict
        The available filters to be parsed.

    Returns:
    --------
    dict
        A dictionary containing the parsed filters.
    """
    parsed_filters: dict = {}

    if source_types := filters.get("source_types"):
        parsed_filters["source_types"] = parse_source_type_filter(source_types)
    if scimago_quartiles := filters.get("scimago_quartiles"):
        parsed_filters["scimago_quartiles"] = parse_scimago_quartile_filter(scimago_quartiles)

    return parsed_filters


def parse_source_type_filter(source_types: list) -> list:
    """
    Parses the source type filter from the search results.

    Parameters
    ----------
    source_types : list
        The source type filter to be parsed.

    Returns
    -------
    list
        A list containing the parsed source type filter.
    """
    parsed_sources: list = []

    for source_doc in source_types:
        source_id = source_doc.get("_id")
        if not source_id:
            continue

        types = source_doc.get("types", [])
        type_counts = {}

        for t in types:
            raw_type = t.get("type")
            count = t.get("count", 0)

            if not raw_type:
                continue

            normalized = NORMALIZED_TYPE_MAPPING.get(raw_type, "other")
            type_counts[normalized] = type_counts.get(normalized, 0) + count

        children = []
        for normalized_type, total_count in type_counts.items():
            title = TYPE_DISPLAY_MAPPING.get(normalized_type, normalized_type)
            value = f"{source_id}_{title}"

            children.append(
                {
                    "value": value,
                    "title": title,
                    "count": total_count,
                }
            )

        children.sort(key=lambda c: c["count"], reverse=True)

        parsed_sources.append(
            {"value": source_id, "title": SOURCE_TITLES.get(source_id, source_id), "children": children}
        )

    parsed_sources.sort(key=lambda s: s["title"])

    return parsed_sources


def parse_scimago_quartile_filter(quartiles: list) -> list:
    """
    Parses the Scimago quartile filter from the search results.

    Parameters
    ----------
    quartiles : list
        The Scimago quartile filter to be parsed.

    Returns
    -------
    list
        A list containing the parsed Scimago quartile filter.
    """
    parsed_quartiles: list = []

    quartile_order = ["Q1", "Q2", "Q3", "Q4", "-"]
    quartile_dict = {q.get("_id"): q.get("count", 0) for q in quartiles if q.get("_id")}

    for quartile in quartile_order:
        if quartile in quartile_dict:
            title = QUARTILE_MAPPING.get(quartile, quartile)
            parsed_quartiles.append({"value": quartile, "title": title, "count": quartile_dict[quartile]})

    return parsed_quartiles
