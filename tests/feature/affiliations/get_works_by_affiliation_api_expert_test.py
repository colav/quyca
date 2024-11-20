def test_get_works_by_institution_api_expert(client, random_institution_id):
    response = client.get(
        f"/affiliation/institution/{random_institution_id}/research/products?max=10&page=1&sort=citations_desc"
    )
    assert response.status_code == 200


def test_get_works_by_faculty_api_expert(client, random_faculty_id):
    response = client.get(
        f"/affiliation/faculty/{random_faculty_id}/research/products?max=10&page=1&sort=citations_desc"
    )
    assert response.status_code == 200


def test_get_works_by_department_api_expert(client, random_department_id):
    response = client.get(
        f"/affiliation/department/{random_department_id}/research/products?max=10&page=1&sort=citations_desc"
    )
    assert response.status_code == 200


def test_get_works_by_group_api_expert(client, random_group_id):
    response = client.get(f"/affiliation/group/{random_group_id}/research/products?max=10&page=1&sort=citations_desc")
    assert response.status_code == 200
