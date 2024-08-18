from bson import ObjectId

from models.affiliation_calculations_model import AffiliationCalculations
from models.person_calculations_model import PersonCalculations
from repositories.mongo import calculations_database


class CalculationsRepository:

    @staticmethod
    def get_person_calculations(person_id: str) -> PersonCalculations:
        person_calculations = calculations_database["person"].find_one({"_id": ObjectId(person_id)})

        return PersonCalculations(**person_calculations)

    @staticmethod
    def get_affiliation_calculations(affiliation_id: str) -> AffiliationCalculations:
        affiliation_calculations = calculations_database["affiliations"].find_one({"_id": ObjectId(affiliation_id)})

        return AffiliationCalculations(**affiliation_calculations)