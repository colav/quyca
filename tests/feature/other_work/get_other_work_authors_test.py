from quyca.database.mongo import database

random_other_work_id = database["works_misc"].aggregate([{"$sample": {"size": 1}}]).next()["_id"]


def test_it_can_get_other_work_authors(client):
    response = client.get(f"/app/other_work/{random_other_work_id}/authors")
    assert response.status_code == 200