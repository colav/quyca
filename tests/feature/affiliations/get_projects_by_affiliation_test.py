def test_get_projects_by_institution(client, random_institution_id):
    response = client.get(f"/app/affiliation/institution/{random_institution_id}/research/projects")
    assert response.status_code == 200


def test_get_projects_by_faculty(client, random_faculty_id):
    response = client.get(f"/app/affiliation/faculty/{random_faculty_id}/research/projects")
    assert response.status_code == 200


def test_get_projects_by_department(client, random_department_id):
    response = client.get(f"/app/affiliation/department/{random_department_id}/research/projects")
    assert response.status_code == 200


def test_get_projects_by_group(client, random_group_id):
    response = client.get(f"/app/affiliation/group/{random_group_id}/research/projects")
    assert response.status_code == 200
