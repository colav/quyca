def test_it_can_plot_citations_by_department_by_institution(client, random_institution_id):
    response = client.get(
        f"/app/affiliation/institution/{random_institution_id}/research/products?plot=citations_by_department"
    )
    assert response.status_code == 200


def test_it_can_plot_citations_by_department_by_faculty(client, random_faculty_id):
    response = client.get(
        f"/app/affiliation/faculty/{random_faculty_id}/research/products?plot=citations_by_department"
    )
    assert response.status_code == 200
