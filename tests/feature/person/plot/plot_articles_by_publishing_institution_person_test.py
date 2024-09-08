from database.mongo import database

random_person_id = (
    database["person"].aggregate([{"$sample": {"size": 1}}]).next()["_id"]
)


def test_it_can_plot_articles_by_publishing_institution_by_person(client):
    response = client.get(
        f"/app/person/{random_person_id}/research/products?plot=articles_by_publishing_institution"
    )

    assert response.status_code == 200