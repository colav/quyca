def test_search_works(client) -> None:
    response = client.get(f"/app/search/works?keywords=quantum&max=10&page=10&sort=citations_desc")
    assert response.status_code == 200


def test_search_works_without_keywords(client) -> None:
    response = client.get(f"/app/search/works?max=10&page=10&sort=citations_desc")
    assert response.status_code == 200


def test_search_works_with_filters(client) -> None:
    response = client.get(
        f"/app/search/works?keywords=quantum&product_type=scholar_article,scienti_Publicado en revista especializada"
    )
    assert response.status_code == 200


def test_search_works_without_keywords_with_filters(client) -> None:
    response = client.get(
        f"/app/search/works?max=10&page=10&product_type=scholar_article,scienti_Publicado en revista especializada"
    )
    assert response.status_code == 200
