from bson import ObjectId

from exceptions.person_exception import PersonException
from models.person_model import Person
from repositories.calculations_repository import CalculationsRepository
from repositories.mongo import database
from repositories.work_repository import WorkRepository


class PersonRepository:
    person_collection = database["person"]

    @staticmethod
    def get_by_id(person_id: str) -> Person:
        person_data = PersonRepository.person_collection.find_one({"_id": ObjectId(person_id)})

        if person_data is None:
            raise PersonException(person_id)

        person_calculations = CalculationsRepository.get_person_calculations_by_person_id(person_id)
        person = Person(**person_data)

        person.citations_count = person_calculations.citations_count
        person.products_count = WorkRepository.get_works_count_by_person_id(person_id)

        return person
