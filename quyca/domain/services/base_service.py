from urllib.parse import urlparse

from domain.constants.external_urls import external_urls_dict
from domain.models.base_model import Title, ProductType, ExternalUrl
from domain.models.other_work_model import OtherWork
from domain.models.patent_model import Patent
from domain.models.project_model import Project
from domain.models.work_model import Work
from infrastructure.repositories import person_repository


def set_title_and_language(workable: Work | OtherWork | Patent | Project) -> None:
    def order(title: Title) -> float:
        hierarchy = ["openalex", "scholar", "scienti", "minciencias", "ranking"]
        return hierarchy.index(title.source) if title.source in hierarchy else float("inf")

    first_title = sorted(workable.titles, key=order)[0]
    workable.language = first_title.lang
    workable.title = first_title.title


def set_product_types(workable: Work | OtherWork | Patent | Project) -> None:
    def order(product_type: ProductType) -> float:
        hierarchy = ["openalex", "scienti", "minciencias", "scholar"]
        return hierarchy.index(product_type.source) if product_type.source in hierarchy else float("inf")

    def filter_func(product_type: ProductType) -> bool:
        if product_type.source == "minciencias" and product_type.level == 0:
            return False
        elif product_type.source == "scienti" and product_type.level in [0, 1]:
            return False
        return True

    types = filter(filter_func, workable.types)
    product_types = list(map(lambda x: ProductType(name=x.type, source=x.source), types))
    workable.product_types = sorted(product_types, key=order)


def set_authors_external_ids(workable: Work | OtherWork | Patent | Project) -> None:
    if not workable.authors:
        return
    for author in workable.authors:
        if author.id:
            author.external_ids = person_repository.get_person_by_id(str(author.id)).external_ids


def limit_authors(workable: Work | OtherWork | Patent | Project, limit: int = 10) -> None:
    if not workable.authors:
        return
    if len(workable.authors) > limit:
        workable.authors = workable.authors[:limit]


def set_external_ids(workable: Work | OtherWork | Patent | Project) -> None:
    if not workable.external_ids:
        return
    new_external_ids = []
    for external_id in workable.external_ids:
        if external_id.source in ["minciencias", "scienti"]:
            new_external_ids.append(external_id)
        else:
            workable.external_urls.append(ExternalUrl(url=external_id.id, source=external_id.source))
    workable.external_ids = list(set(new_external_ids))


def set_external_urls(workable: Work | OtherWork | Patent | Project) -> None:
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
