from pymongo.cursor import Cursor

from models.person_model import Person


class PersonGenerator:
   @staticmethod
   def get(cursor: Cursor):
       for document in cursor:
           yield Person(**document)