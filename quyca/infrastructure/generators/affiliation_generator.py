from typing import Generator

from pymongo.command_cursor import CommandCursor

from quyca.domain.models.affiliation_model import Affiliation


def get(cursor: CommandCursor) -> Generator["Affiliation", None, None]:
    for document in cursor:
        yield Affiliation(**document)
