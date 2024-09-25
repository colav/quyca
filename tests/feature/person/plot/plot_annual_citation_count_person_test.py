from quyca.infrastructure.mongo import database

random_person_id = database["person"].aggregate([{"$sample": {"size": 1}}]).next()["_id"]


def test_it_can_plot_annual_citation_count_by_person(client):
    response = client.get(f"/app/person/{random_person_id}/research/products?plot=annual_citation_count")

    assert response.status_code == 200
