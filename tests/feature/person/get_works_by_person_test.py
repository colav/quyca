from quyca.infrastructure.mongo import database


def test_get_works_by_person(client):
    random_person_id = database["person"].aggregate([{"$sample": {"size": 1}}]).next()["_id"]
    response = client.get(f"/app/person/{random_person_id}/research/products?max=10&page=2&sort=citations_desc")
    assert response.status_code == 200
