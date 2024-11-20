def test_get_institution_by_id(client, random_institution_id):
    response = client.get(f"/app/affiliation/institution/{random_institution_id}")
    assert response.status_code == 200


def test_get_faculty_by_id(client, random_faculty_id):
    response = client.get(f"/app/affiliation/faculty/{random_faculty_id}")
    assert response.status_code == 200


def test_get_department_by_id(client, random_department_id):
    response = client.get(f"/app/affiliation/department/{random_department_id}")
    assert response.status_code == 200


def test_get_group_by_id(client, random_group_id):
    response = client.get(f"/app/affiliation/group/{random_group_id}")
    assert response.status_code == 200
