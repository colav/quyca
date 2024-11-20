def test_it_can_plot_active_authors_by_age_range_by_institution(client, random_institution_id):
    response = client.get(
        f"/app/affiliation/institution/{random_institution_id}/research/products?plot=active_authors_by_age_range"
    )
    assert response.status_code == 200


def test_it_can_plot_active_authors_by_age_range_by_faculty(client, random_faculty_id):
    response = client.get(
        f"/app/affiliation/faculty/{random_faculty_id}/research/products?plot=active_authors_by_age_range"
    )
    assert response.status_code == 200


def test_it_can_plot_active_authors_by_age_range_by_department(client, random_department_id):
    response = client.get(
        f"/app/affiliation/department/{random_department_id}/research/products?plot=active_authors_by_age_range"
    )
    assert response.status_code == 200


def test_it_can_plot_active_authors_by_age_range_by_group(client, random_group_id):
    response = client.get(
        f"/app/affiliation/group/{random_group_id}/research/products?plot=active_authors_by_age_range"
    )
    assert response.status_code == 200
