def test_it_can_plot_research_groups_by_product_type_by_institution(client, random_institution_id):
    response = client.get(
        f"/app/affiliation/institution/{random_institution_id}/research/products?plot=research_groups_by_product_type"
    )
    assert response.status_code == 200


def test_it_can_plot_research_groups_by_product_type_by_faculty(client, random_faculty_id):
    response = client.get(
        f"/app/affiliation/faculty/{random_faculty_id}/research/products?plot=research_groups_by_product_type"
    )
    assert response.status_code == 200


def test_it_can_plot_research_groups_by_product_type_by_department(client, random_department_id):
    response = client.get(
        f"/app/affiliation/department/{random_department_id}/research/products?plot=research_groups_by_product_type"
    )
    assert response.status_code == 200
