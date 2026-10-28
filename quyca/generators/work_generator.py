from typing import Generator

from pymongo.command_cursor import CommandCursor

from quyca.domain.models.work_model import Work


def get(cursor: CommandCursor) -> Generator:
    for document in cursor:
        try:
            yield Work(**document)
        except Exception as e:
            print("Validation error while parsing Work document _id=%s", e)
            raise
