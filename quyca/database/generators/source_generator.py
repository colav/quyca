from typing import Generator

from pymongo.command_cursor import CommandCursor

from database.models.source_model import Source


def get(cursor: CommandCursor) -> Generator:
    for document in cursor:
        yield Source(**document)
