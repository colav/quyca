import csv
import io
from typing import Generator


from domain.constants.product_types import source_titles
from domain.models.work_model import Work


def parse_csv(works: list) -> str:
    include = [
        "title",
        "language",
        "abstract",
        "authors",
        "institutions",
        "faculties",
        "departments",
        "groups",
        "countries",
        "groups_ranking",
        "ranking",
        "issue",
        "open_access",
        "pages",
        "start_page",
        "end_page",
        "volume",
        "bibtex",
        "scimago_quartile",
        "openalex_citations_count",
        "scholar_citations_count",
        "subjects",
        "year_published",
        "doi",
        "publisher",
        "openalex_types",
        "scienti_types",
        "source_name",
        "source_apc",
        "source_urls",
    ]
    works_dict = [work.model_dump(include=include) for work in works]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=include)
    writer.writeheader()
    writer.writerows(works_dict)
    return output.getvalue()


def parse_search_results(works: list) -> list:
    include = [
        "id",
        "authors",
        "authors_count",
        "open_access",
        "citations_count",
        "product_types",
        "year_published",
        "title",
        "subjects",
        "source",
        "external_ids",
        "external_urls",
    ]
    return [work.model_dump(include=include, exclude_none=True) for work in works]


def parse_works_by_entity(works: list) -> list:
    include = [
        "id",
        "authors",
        "authors_count",
        "open_access",
        "citations_count",
        "product_types",
        "year_published",
        "title",
        "subjects",
        "source",
        "external_ids",
    ]
    return [work.model_dump(include=include, exclude_none=True) for work in works]


def parse_work(work: Work) -> dict:
    return work.model_dump(exclude_none=True)


def parse_api_expert(works: Generator) -> list:
    return [work.model_dump(exclude_none=True) for work in works]


def parse_available_filters(filters: dict) -> dict:
    available_filters: dict = {}
    if product_types := filters.get("product_types"):
        types = []
        for product_type in product_types:
            if product_type.get("_id") == "crossref":
                continue
            children = []
            for inner_type in product_type.get("types"):
                children.append({"value": product_type.get("_id") + "_" + inner_type, "title": inner_type})
            types.append(
                {
                    "value": product_type.get("_id"),
                    "title": source_titles.get(product_type.get("_id")),
                    "children": children,
                }
            )
        available_filters["product_types"] = types
    return available_filters
