from quyca.infrastructure.mongo import database


def test_it_can_plot_articles_by_scimago_quartile_by_institution(client):
    random_person_id = database["person"].aggregate([{"$sample": {"size": 1}}]).next()["_id"]
    response = client.get(f"/app/person/{random_person_id}/research/products?plot=articles_by_scimago_quartile")
    assert response.status_code == 200
