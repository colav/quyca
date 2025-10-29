from quyca.infrastructure.mongo import database


def test_search_sources_without_params(client):
    response = client.get("/search/sources", follow_redirects=True)

    assert response.status_code == 200
    data = response.get_json()

    assert "data" in data
    assert "total_results" in data
    assert isinstance(data["data"], list)
    assert isinstance(data["total_results"], int)
    assert data["total_results"] > 0


def test_search_sources_with_pagination(client):
    response = client.get("/search/sources?max=5&page=1", follow_redirects=True)

    assert response.status_code == 200
    data = response.get_json()

    assert len(data["data"]) <= 5
    assert data["total_results"] >= len(data["data"])


def test_search_sources_with_keywords(client):
    sample_source = database["sources"].aggregate([{"$sample": {"size": 1}}, {"$project": {"name": 1}}]).next()

    if sample_source.get("name"):
        keyword = sample_source["name"].split()[0]
        response = client.get(f"/search/sources?keywords={keyword}", follow_redirects=True)

        assert response.status_code == 200
        data = response.get_json()

        assert "data" in data
        assert isinstance(data["data"], list)


def test_search_sources_with_multiple_filters(client):
    response = client.get("/search/sources?max=10&page=1&keywords=science", follow_redirects=True)

    assert response.status_code == 200
    data = response.get_json()

    assert "data" in data
    assert "total_results" in data
    assert len(data["data"]) <= 10


def test_search_sources_pagination_limits(client):
    response = client.get("/search/sources?max=250&page=1", follow_redirects=True)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]) <= 250

    response = client.get("/search/sources?max=300&page=1", follow_redirects=True)
    assert response.status_code in [200, 400]


def test_search_sources_page_beyond_results(client):
    response = client.get("/search/sources?max=10&page=99999", follow_redirects=True)

    assert response.status_code == 200
    data = response.get_json()

    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 0


def test_search_sources_sort_parameter(client):
    response = client.get("/search/sources?max=10&page=1&sort=alphabetical_asc", follow_redirects=True)

    assert response.status_code == 200
    data = response.get_json()

    assert "data" in data
    assert isinstance(data["data"], list)


def test_search_sources_redirect_from_api_endpoint(client):
    response = client.get("/search/sources?max=10&page=1", follow_redirects=False)

    assert response.status_code == 302

    response_redirected = client.get("/search/sources?max=10&page=1", follow_redirects=True)
    assert response_redirected.status_code == 200
    data = response_redirected.get_json()
    assert "data" in data
    assert "total_results" in data
