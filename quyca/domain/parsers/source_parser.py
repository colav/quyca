from typing import List

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
