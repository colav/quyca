from quyca.infrastructure.mongo import database


def test_get_other_news_by_person_id(client):
    random_person_id = database["person"].aggregate([{"$sample": {"size": 1}}, {"$project": {"_id": 1}}]).next()["_id"]
    response = client.get(f"/app/person/{random_person_id}/research/news?max=100")
    assert response.status_code == 200
