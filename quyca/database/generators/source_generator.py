from pymongo.cursor import Cursor

from database.models.source_model import Source


def get(cursor: Cursor):
   for document in cursor:
       yield Source(**document)