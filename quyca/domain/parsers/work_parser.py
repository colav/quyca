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
    writer = csv.DictWriter(output, fieldnames=include, escapechar="\\", quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    writer.writerows(works_dict)
    del works_dict
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
            if product_type.get("_id") == "scienti":
                second_level_children = []
                third_level_children = []
                for inner_type in product_type.get("types"):
                    if inner_type.get("level") == 0:
                        children.append(
                            {
                                "value": "scienti_" + inner_type.get("type") + "_" + inner_type.get("code"),
                                "title": inner_type.get("code") + " " + inner_type.get("type"),
                                "code": inner_type.get("code"),
                                "children": [],
                            }
                        )
                    elif inner_type.get("level") == 1:
                        second_level_children.append(
                            {
                                "value": "scienti_" + inner_type.get("type") + "_" + inner_type.get("code"),
                                "title": inner_type.get("code") + " " + inner_type.get("type"),
                                "code": inner_type.get("code"),
                                "children": [],
                            }
                        )
                    elif inner_type.get("level") == 2:
                        third_level_children.append(
                            {
                                "value": "scienti_" + inner_type.get("type") + "_" + inner_type.get("code"),
                                "title": inner_type.get("code") + " " + inner_type.get("type"),
                                "code": inner_type.get("code"),
                            }
                        )
                second_level_children.sort(key=lambda x: x.get("title"))  # type: ignore
                third_level_children.sort(key=lambda x: x.get("title"))  # type: ignore
                for child in second_level_children:
                    child["children"] = list(
                        filter(lambda x: str(x.get("code")).startswith(str(child.get("code"))), third_level_children)
                    )
                for child in children:
                    child["children"] = list(
                        filter(lambda x: str(x.get("code")).startswith(str(child.get("code"))), second_level_children)
                    )
            else:
                for inner_type in product_type.get("types"):
                    children.append(
                        {
                            "value": product_type.get("_id") + "_" + inner_type.get("type"),
                            "title": inner_type.get("type"),
                        }
                    )
            children.sort(key=lambda x: x.get("title"))  # type: ignore
            types.append(
                {
                    "value": product_type.get("_id"),
                    "title": source_titles.get(product_type.get("_id")),
                    "children": children,
                }
            )
        available_filters["product_types"] = types
    return available_filters
