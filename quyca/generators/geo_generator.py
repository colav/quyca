from typing import Generator

from pymongo.command_cursor import CommandCursor

from quyca.models.geo_model import Geo


def get(cursor: CommandCursor) -> Generator:
    for document in cursor:
        try:
            if isinstance(document, Geo):
                yield document
            else:
                yield Geo(**document)
        except Exception as e:
            print("Validation error while parsing Geolocation document _id=%s", e)
            raise
