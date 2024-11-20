def test_get_related_affiliations_by_institution(client, random_institution_id):
    response = client.get(f"/app/affiliation/institution/{random_institution_id}/affiliations")
    assert response.status_code == 200


def test_get_related_affiliations_by_faculty(client, random_faculty_id):
    response = client.get(f"/app/affiliation/faculty/{random_faculty_id}/affiliations")
    assert response.status_code == 200


def test_get_related_affiliations_by_department(client, random_department_id):
    response = client.get(f"/app/affiliation/department/{random_department_id}/affiliations")
    assert response.status_code == 200


def test_get_related_affiliations_by_group(client, random_group_id):
    response = client.get(f"/app/affiliation/group/{random_group_id}/affiliations")
    assert response.status_code == 200
