from repositories.mongo import database

random_institution_id = database['affiliations'].aggregate([{ '$sample': { 'size': 1 } }]).next()["_id"]
random_affiliation_id = database['affiliations'].aggregate([
    { "$match": {"types.type": "faculty"}},
    { '$sample': { 'size': 1 } }
]).next()["_id"]



def test_it_can_plot_collaboration_network_by_institution(client):
    response = client.get(
        f"/app/affiliation/institution/{random_institution_id}/research/products?plot=collaboration_network"
    )

    assert response.status_code == 200


def test_it_can_plot_collaboration_network_by_faculty(client):
    response = client.get(
        f"/app/affiliation/faculty/{random_affiliation_id}/research/products?plot=collaboration_network"
    )

    assert response.status_code == 200


def test_it_can_plot_collaboration_network_by_department(client):
    response = client.get(
        f"/app/affiliation/department/{random_affiliation_id}/research/products?plot=collaboration_network"
    )

    assert response.status_code == 200


def test_it_can_plot_collaboration_network_by_group(client):
    response = client.get(
        f"/app/affiliation/group/{random_affiliation_id}/research/products?plot=collaboration_network"
    )

    assert response.status_code == 200
