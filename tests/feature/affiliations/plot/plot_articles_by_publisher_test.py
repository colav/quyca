from database.mongo import database

random_affiliation_id = (
    database["affiliations"].aggregate([{"$sample": {"size": 1}}]).next()["_id"]
)


def test_it_can_plot_articles_by_publisher_by_institution(client):
    response = client.get(
        f"/app/affiliation/institution/{random_affiliation_id}/research/products?plot=articles_by_publisher"
    )

    assert response.status_code == 200


def test_it_can_plot_articles_by_publisher_by_faculty(client):
    response = client.get(
        f"/app/affiliation/faculty/{random_affiliation_id}/research/products?plot=articles_by_publisher"
    )

    assert response.status_code == 200


def test_it_can_plot_articles_by_publisher_by_department(client):
    response = client.get(
        f"/app/affiliation/department/{random_affiliation_id}/research/products?plot=articles_by_publisher"
    )

    assert response.status_code == 200


def test_it_can_plot_articles_by_publisher_by_group(client):
    response = client.get(
        f"/app/affiliation/group/{random_affiliation_id}/research/products?plot=articles_by_publisher"
    )

    assert response.status_code == 200
