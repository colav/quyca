def test_it_can_plot_faculties_by_product_type_by_institution(client, random_institution_id):
    response = client.get(
        f"/app/affiliation/institution/{random_institution_id}/research/products?plot=faculties_by_product_type"
    )
    assert response.status_code == 200
