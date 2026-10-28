from typing import Generator

from quyca.files import tabular_writer_exporter
from quyca.repositories import apc_repository, base_repository


def get_apc_csv_by_search(keywords: str | None) -> Generator[str, None, None]:
    return _get_apc_csv(base_repository.text_search_match(keywords))


def get_apc_csv_by_person(person_id: str) -> Generator[str, None, None]:
    return _get_apc_csv([{"$match": {"authors.id": person_id}}])


def get_apc_csv_by_affiliation(affiliation_id: str) -> Generator[str, None, None]:
    return _get_apc_csv([{"$match": {"authors.affiliations.id": affiliation_id}}])


def _get_apc_csv(match_stages: list[dict]) -> Generator[str, None, None]:
    works_apc = apc_repository.get_works_apc(match_stages)
    return tabular_writer_exporter.write_csv(works_apc, apc_repository.APC_COLUMNS)
