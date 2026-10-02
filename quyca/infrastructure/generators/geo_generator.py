from typing import Generator

from pymongo.command_cursor import CommandCursor

from quyca.domain.models.geo_model import Geo


def get(cursor: CommandCursor) -> Generator[Geo, None, None]:
    for document in cursor:
        try:
            yield Geo(**document)
        except Exception as e:
            raise ValueError(f"Validation error while parsing Geo document _id={document.get('_id')}: {e}")
