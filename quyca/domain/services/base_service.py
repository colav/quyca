from typing import Generator, Iterator, Union, Any, Dict, List, Union, cast
from urllib.parse import urlparse
from quyca.domain.constants.institutions import institutions_list
from quyca.domain.constants.summary_rules import (
    AFFILIATION_SUMMARY_FIELDS,
    PATENT_SUMMARY_FIELDS,
    PERSON_SUMMARY_FIELDS,
    PROJECT_SUMMARY_FIELDS,
    SOURCE_SUMMARY_FIELDS,
    WORK_SUMMARY_FIELDS,
)
from quyca.domain.models.affiliation_model import Affiliation, Relation
from quyca.domain.constants.external_urls import external_urls_dict
from quyca.domain.models.base_model import Title, ProductType, ExternalUrl, Type
from quyca.domain.models.patent_model import Patent
from quyca.domain.models.project_model import Project
from quyca.domain.models.work_model import Work, Source as WorkSource
from quyca.infrastructure.repositories.person import person_repository
from quyca.domain.constants.sensitive_data import SENSITIVE_ID_SOURCES
from quyca.infrastructure.repositories.affiliation import affiliation_repository

SUMMARY_AUTHORS_LIMIT = 10

def get_entity_data(documents: Generator, view: str = "full") -> list:
    authors_limit = SUMMARY_AUTHORS_LIMIT if view == "summary" else None
    data = []
    for doc in documents:
        limit_authors(doc, authors_limit)
        set_title_and_language(doc)
        set_product_types(doc)
        set_authors_affiliation_years(doc)
        data.append(doc)
    return data


def get_affiliation_by_entity_data(affiliation_type: str, affiliations: Generator) -> list:
    affiliations_list = []
    for affiliation in affiliations:
        set_relation_external_urls(affiliation)
        set_upper_affiliations_and_logo(affiliation, affiliation_type)
        affiliations_list.append(affiliation)
    return affiliations_list


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

    def filter_func(product_type: Type) -> bool:
        if product_type.source == "minciencias" and product_type.level == 0:
            return False
        if product_type.source == "scienti":
            if 2 in scienti_levels:
                return (product_type.level or 0) >= 2
            else:
                return (product_type.level or 0) >= 1
        return True

    types: Iterator[Type] = filter(filter_func, workable.types or [])
    product_types: list[ProductType] = [ProductType(name=x.type, source=x.source) for x in types]
    workable.product_types = sorted(product_types, key=order)


def set_authors_external_ids(workable: Union[Work, Patent, Project], filter_sensitive: bool = False) -> None:
    if not workable.authors:
        return

    if isinstance(workable.authors, str):
        return

    for author in workable.authors:
        if author.id:
            external_ids = person_repository.get_person_external_ids(str(author.id))
            if filter_sensitive:
                external_ids = [eid for eid in external_ids if eid.source not in SENSITIVE_ID_SOURCES]
            author.external_ids = external_ids



def limit_authors(workable: Union[Work, Patent, Project], limit: int | None = None) -> None:
    if not workable.authors or limit is None:
        return
    if isinstance(workable.authors, str):
        return
    if len(workable.authors) > limit:
        workable.authors = workable.authors[:limit]


def set_external_ids(workable: Union[Work, Patent, Project], filter_sensitive: bool = False) -> None:
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


def set_relation_external_urls(affiliation: Affiliation) -> None:
    if not affiliation.relations:
        return

    if isinstance(affiliation.relations, (list, tuple)):
        relations_iterable = affiliation.relations
    elif isinstance(affiliation.relations, dict):
        relations_iterable = [Relation(**affiliation.relations)]
    elif isinstance(affiliation.relations, Relation):
        relations_iterable = [affiliation.relations]
    else:
        return

    for relation in relations_iterable:
        if not isinstance(relation, Relation):
            continue

        if getattr(relation, "external_urls", None):
            continue

        relation_external_urls = None

        if getattr(relation, "id", None):
            try:
                related_aff = affiliation_repository.get_affiliation_by_id(str(relation.id))
                if getattr(related_aff, "external_urls", None):
                    relation_external_urls = related_aff.external_urls
            except Exception:
                relation_external_urls = None

        relation.external_urls = relation_external_urls or []


def set_upper_affiliations_and_logo(affiliation: Affiliation, affiliation_type: str) -> None:
    if affiliation_type == "institution" and affiliation.external_urls:
        logo_url = next(
            (x.url for x in affiliation.external_urls if x.source == "logo"),
            None,
        )
        if logo_url:
            affiliation.logo = str(logo_url)

    relations_iterable: List[Relation]
    if isinstance(affiliation.relations, (list, tuple)):
        relations_iterable = affiliation.relations
    elif isinstance(affiliation.relations, Dict):
        relations_iterable = [Relation(**affiliation.relations)]
    elif isinstance(affiliation.relations, Relation):
        relations_iterable = [affiliation.relations]
    else:
        affiliation.affiliations = []
        return

    upper_affiliations: list[Relation] = []
    if not affiliation.relations:
        affiliation.affiliations = []
        return

    for relation in relations_iterable:
        if not isinstance(relation, Relation):
            continue
        if not relation.types:
            continue

        first_type = relation.types[0].type

        if affiliation_type == "faculty" and first_type in institutions_list:
            set_logo(affiliation, relation)
            upper_affiliations.append(relation)

        elif affiliation_type == "department" and first_type in institutions_list + ["faculty"]:
            set_logo(affiliation, relation)
            upper_affiliations.append(relation)

        elif affiliation_type == "group" and first_type in institutions_list + ["department", "faculty"]:
            set_logo(affiliation, relation)
            upper_affiliations.append(relation)

    affiliation.affiliations = cast(List[Union[Dict[Any, Any], Relation]], upper_affiliations) or []


def set_logo(affiliation: Affiliation, relation: Relation) -> None:
    if not relation.types or not relation.external_urls:
        return
    if relation.types[0].type in institutions_list:
        logo_url = next(
            (x.url for x in relation.external_urls if x.source == "logo"),
            None,
        )
        if logo_url:
            affiliation.logo = str(logo_url)


def update_csv_work_source(work: Work) -> None:
    if not work.source:
        return

    source = work.source
    work.source_name = str(source.name) if source.name else None
    if source.apc and source.apc.charges and source.apc.currency:
        work.source_apc = f"{source.apc.charges} / {source.apc.currency}"
    else:
        work.source_apc = None

    set_source_urls(work, source)
    set_scimago_quartile(work, source)


def set_source_urls(work: Work, source: WorkSource) -> None:
    if source.external_urls:
        urls = {str(url.url) for url in source.external_urls if url.url}
        work.source_urls = " | ".join(urls) if urls else None
    else:
        work.source_urls = None


def set_scimago_quartile(work: Work, source: WorkSource) -> None:
    work.scimago_quartile = None
    if source.ranking and work.date_published:
        for ranking in source.ranking:
            condition = (
                ranking.source == "scimago Best Quartile"
                and ranking.rank
                and ranking.rank != "-"
                and isinstance(ranking.from_date, int)
                and isinstance(ranking.to_date, int)
                and ranking.from_date <= work.date_published <= ranking.to_date
            )
            if condition:
                work.scimago_quartile = str(ranking.rank)
                break


def set_authors_affiliation_years(docs: list | Work | Patent | Project) -> None:
    if not isinstance(docs, list):
        docs = [docs]
    person_ids = {a.id for d in docs for a in (d.authors or []) if a.id}
    years_by_person = person_repository.get_affiliation_years(person_ids)
    for doc in docs:
        for author in doc.authors or []:
            author_years = years_by_person.get(author.id, {})
            for aff in author.affiliations or []:
                aff.years = author_years.get(aff.id, [])


def build_work_pipeline_params(view: str = "full") -> dict:
    if view == "summary":
        return {"project": WORK_SUMMARY_FIELDS}
    return {}


def build_person_pipeline_params(view: str = "full") -> dict:
    if view == "summary":
        return {"project": PERSON_SUMMARY_FIELDS}
    return {}


def build_affiliation_pipeline_params(view: str = "full") -> dict:
    if view == "summary":
        return {"project": AFFILIATION_SUMMARY_FIELDS}
    return {}


def build_patents_pipeline_params(view: str = "full") -> dict:
    if view == "summary":
        return {"project": PATENT_SUMMARY_FIELDS}
    return {}


def build_projects_pipeline_params(view: str = "full") -> dict:
    if view == "summary":
        return {"project": PROJECT_SUMMARY_FIELDS}
    return {}


def build_sources_pipeline_params(view: str = "full") -> dict:
    if view == "summary":
        return {"project": SOURCE_SUMMARY_FIELDS, "collection": "sources"}
    return {}
