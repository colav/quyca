from bson import ObjectId

from database.models.affiliation_calculations_model import Calculations
from database.mongo import calculations_database


def get_person_calculations(person_id: str) -> Calculations:
    person_calculations = calculations_database["person"].find_one({"_id": ObjectId(person_id)})
    if not person_calculations:
        return Calculations()
    return Calculations(**person_calculations)


def get_affiliation_calculations(affiliation_id: str) -> Calculations:
    affiliation_calculations = calculations_database["affiliations"].find_one({"_id": ObjectId(affiliation_id)})
    if not affiliation_calculations:
        return Calculations()
    return Calculations(**affiliation_calculations)
