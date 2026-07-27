from typing import List

from quyca.domain.models.base_model import Affiliation


def parse_search_result(affiliations: List) -> List[Affiliation]:
    include = [
        "id",
        "addresses",
        "affiliations",
        "external_ids",
        "external_urls",
        "products_count",
        "citations_count",
        "h_index",
        "h5_index",
        "logo",
        "name",
        "types",
        "products_count",
        "ranking",
    ]
    return [affiliation.model_dump(include=include, exclude_none=True) for affiliation in affiliations]
