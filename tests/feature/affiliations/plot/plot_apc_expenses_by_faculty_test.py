def test_it_can_plot_apc_expenses_by_faculty_by_institution(client, random_institution_id):
    response = client.get(
        f"/app/affiliation/institution/{random_institution_id}/research/products?plot=apc_expenses_by_faculty"
    )
    assert response.status_code == 200
