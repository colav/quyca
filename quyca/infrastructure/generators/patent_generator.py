from typing import Generator

from pymongo.command_cursor import CommandCursor

from domain.models.patent_model import Patent


def get(cursor: CommandCursor) -> Generator:
    for document in cursor:
        yield Patent(**document)
