from typing import Generator

from pymongo.command_cursor import CommandCursor

from quyca.domain.models.project_model import Project


def get(cursor: CommandCursor) -> Generator:
    for document in cursor:
        yield Project(**document)
