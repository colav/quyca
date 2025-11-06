from typing import Iterator, List, Type, Union
from urllib.parse import urlparse

from quyca.domain.constants.external_urls import external_urls_dict
from quyca.domain.models.base_model import Title, ProductType, ExternalUrl
from quyca.domain.models.patent_model import Patent
from quyca.domain.models.project_model import Project
from quyca.domain.models.work_model import Work
from quyca.infrastructure.repositories import person_repository


def set_title_and_language(workable: Union[Work, Patent, Project]) -> None:
    if not workable.titles:
        workable.title = None
        workable.language = None
        return

    hierarchy = ["openalex", "scienti", "minciencias", "ranking", "scholar"]

    def order(title: Title) -> float:
        return hierarchy.index(title.source) if title.source in hierarchy else float("inf")

    first_title = min(workable.titles, key=order)
    workable.title = first_title.title
    workable.language = first_title.lang


def set_product_types(workable: Union[Work, Patent, Project]) -> None:
    def order(product_type: ProductType) -> float:
        hierarchy = ["openalex", "scienti", "minciencias", "scholar"]
        return hierarchy.index(product_type.source) if product_type.source in hierarchy else float("inf")

    scienti_levels = {ptype.level for ptype in workable.types or [] if ptype.source == "scienti"}

    def filter_func(product_type: ProductType) -> bool:
        if product_type.source == "minciencias" and product_type.level == 0:
            return False
        if product_type.source == "scienti":
            if 2 in scienti_levels:
                return (product_type.level or 0) >= 2
            else:
                return (product_type.level or 0) >= 1
        return True

    types: Iterator[Type] = filter(filter_func, workable.types or [])
    product_types: List[ProductType] = list(map(lambda x: ProductType(name=x.type, source=x.source), types))
    workable.product_types = sorted(product_types, key=order)


def set_authors_external_ids(workable: Union[Work, Patent, Project]) -> None:
    if not workable.authors:
        return

    if isinstance(workable.authors, str):
        return

    for author in workable.authors:
        if author.id:
            author.external_ids = person_repository.get_person_by_id(str(author.id)).external_ids


def limit_authors(workable: Union[Work, Patent, Project], limit: int = 10) -> None:
    if not workable.authors:
        return
    if len(workable.authors) > limit:
        workable.authors = workable.authors[:limit]


def set_external_ids(workable: Union[Work, Patent, Project]) -> None:
    if not workable.external_ids:
        return

    if workable.external_urls is None:
        workable.external_urls = []

    new_external_ids = []
    for external_id in workable.external_ids:
        if external_id.source in ["minciencias", "scienti"]:
            new_external_ids.append(external_id)
        else:
            url_value = str(external_id.id)
            workable.external_urls.append(ExternalUrl(url=url_value, source=external_id.source))
    workable.external_ids = list(set(new_external_ids))


def set_external_urls(workable: Union[Work, Patent, Project]) -> None:
    if not workable.external_urls:
        return
    new_external_urls = []
    for external_url in workable.external_urls:
        url = str(external_url.url)
        if urlparse(url).scheme and urlparse(url).netloc:
            new_external_urls.append(external_url)
        else:
            if external_url.source in external_urls_dict.keys() and url != "":
                new_external_urls.append(
                    ExternalUrl(
                        url=external_urls_dict[external_url.source].format(id=url),
                        source=external_url.source,
                    )
                )
    workable.external_urls = list(set(new_external_urls))
