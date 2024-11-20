def test_it_can_plot_citations_by_research_group_by_institution(client, random_institution_id):
    response = client.get(
        f"/app/affiliation/institution/{random_institution_id}/research/products?plot=citations_by_research_group"
    )
    assert response.status_code == 200


def test_it_can_plot_citations_by_research_group_by_faculty(client, random_faculty_id):
    response = client.get(
        f"/app/affiliation/faculty/{random_faculty_id}/research/products?plot=citations_by_research_group"
    )
    assert response.status_code == 200


def test_it_can_plot_citations_by_research_group_by_department(client, random_department_id):
    response = client.get(
        f"/app/affiliation/department/{random_department_id}/research/products?plot=citations_by_research_group"
    )
    assert response.status_code == 200
