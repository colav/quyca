from quyca.infrastructure.mongo import database

random_patent_id = database["patents"].aggregate([{"$sample": {"size": 1}}]).next()["_id"]


def test_it_can_get_patent_authors(client):
    response = client.get(f"/app/patent/{random_patent_id}/authors")
    assert response.status_code == 200
