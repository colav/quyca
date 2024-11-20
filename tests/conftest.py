from pytest import fixture

from infrastructure.mongo import database
from quyca.app import create_app


@fixture()
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )
    yield app


@fixture()
def client(app):
    client = app.test_client()
    yield client


@fixture()
def random_institution_id():
    return (
        database["affiliations"]
        .aggregate([{"$match": {"types.type": "education"}}, {"$sample": {"size": 1}}])
        .next()["hash"]
    )


@fixture()
def random_faculty_id():
    return (
        database["affiliations"]
        .aggregate([{"$match": {"types.type": "faculty"}}, {"$sample": {"size": 1}}])
        .next()["hash"]
    )


@fixture()
def random_department_id():
    return (
        database["affiliations"]
        .aggregate([{"$match": {"types.type": "department"}}, {"$sample": {"size": 1}}])
        .next()["hash"]
    )


@fixture()
def random_group_id():
    return (
        database["affiliations"]
        .aggregate([{"$match": {"types.type": "group"}}, {"$sample": {"size": 1}}])
        .next()["hash"]
    )
