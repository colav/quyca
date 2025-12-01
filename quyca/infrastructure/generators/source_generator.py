from typing import Generator

from pymongo.command_cursor import CommandCursor

from domain.models.source_model import Source


def get(cursor: CommandCursor) -> Generator:
    for document in cursor:
        yield Source(**document)


def generate_sources(sources: list[Source]) -> Generator:
    for source in sources:
        yield source
