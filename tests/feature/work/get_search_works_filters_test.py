def test_search_works(client) -> None:
    response = client.get(f"/app/search/works/filters?keywords=quantum&max=10&page=10&sort=citations_desc")
    assert response.status_code == 200


def test_search_works_without_keywords(client) -> None:
    response = client.get(f"/app/search/works/filters?max=10&page=10&sort=citations_desc")
    assert response.status_code == 200
