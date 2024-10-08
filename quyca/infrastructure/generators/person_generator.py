from typing import Generator

from pymongo.command_cursor import CommandCursor

from domain.models.person_model import Person


def get(cursor: CommandCursor) -> Generator:
    for document in cursor:
        yield Person(**document)
