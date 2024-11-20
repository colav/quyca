def test_it_can_plot_annual_apc_expenses_by_institution(client, random_institution_id):
    response = client.get(
        f"/app/affiliation/faculty/66f6f44899b6ea475f3be53c/affiliations"
    )
    assert response.status_code == 200


def test_it_can_plot_annual_apc_expenses_by_faculty(client, random_faculty_id):
    response = client.get(f"/app/affiliation/faculty/{random_faculty_id}/research/products?plot=annual_apc_expenses")
    assert response.status_code == 200


def test_it_can_plot_annual_apc_expenses_by_department(client, random_department_id):
    response = client.get(
        f"/app/affiliation/department/{random_department_id}/research/products?plot=annual_apc_expenses"
    )
    assert response.status_code == 200


def test_it_can_plot_annual_apc_expenses_by_group(client, random_group_id):
    response = client.get(f"/app/affiliation/group/{random_group_id}/research/products?plot=annual_apc_expenses")
    assert response.status_code == 200
