from quyca.infrastructure.mongo import database


def test_it_can_plot_products_by_subject_by_institution(client):
    random_institution_id = (
        database["affiliations"]
        .aggregate([{"$match": {"types.type": "education"}}, {"$sample": {"size": 1}}])
        .next()["_id"]
    )
    response = client.get(
        f"/app/affiliation/institution/{random_institution_id}/research/products?plot=products_by_subject"
    )
    assert response.status_code == 200


def test_it_can_plot_products_by_subject_by_faculty(client):
    random_faculty_id = (
        database["affiliations"]
        .aggregate([{"$match": {"types.type": "faculty"}}, {"$sample": {"size": 1}}])
        .next()["_id"]
    )
    response = client.get(f"/app/affiliation/faculty/{random_faculty_id}/research/products?plot=products_by_subject")
    assert response.status_code == 200


def test_it_can_plot_products_by_subject_by_department(client):
    random_department_id = (
        database["affiliations"]
        .aggregate([{"$match": {"types.type": "department"}}, {"$sample": {"size": 1}}])
        .next()["_id"]
    )
    response = client.get(
        f"/app/affiliation/department/{random_department_id}/research/products?plot=products_by_subject"
    )
    assert response.status_code == 200


def test_it_can_plot_products_by_subject_by_group(client):
    random_group_id = (
        database["affiliations"]
        .aggregate([{"$match": {"types.type": "group"}}, {"$sample": {"size": 1}}])
        .next()["_id"]
    )
    response = client.get(f"/app/affiliation/group/{random_group_id}/research/products?plot=products_by_subject")
    assert response.status_code == 200
