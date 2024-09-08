import csv
import io


def parse_csv(works: list):
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
        "is_open_access",
        "open_access_status",
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


def parse_search_results(works: list):
    include = [
        "id",
        "authors",
        "is_open_access",
        "open_access_status",
        "citations_count",
        "products_types",
        "year_published",
        "title",
        "subjects",
        "source",
    ]
    return [work.model_dump(include=include, exclude_none=True) for work in works]


def parse_works_by_entity(works: list):
    include = [
        "id",
        "authors",
        "is_open_access",
        "open_access_status",
        "citations_count",
        "products_types",
        "year_published",
        "title",
        "subjects",
        "source",
    ]
    return [work.model_dump(include=include, exclude_none=True) for work in works]
