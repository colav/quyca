from quyca.repositories import source_repository
from quyca.parsers import source_parser


def get_source_by_id(source_id: str) -> dict:
    source = source_repository.get_source_by_id(source_id)
    data = source_parser.parse_source(source)
    return {"data": data}
