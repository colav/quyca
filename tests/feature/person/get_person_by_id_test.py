from quyca.clients.mongo import database
from unittest.mock import patch

from quyca.models.person_model import Person

ENDPOINT = "/person"
random_person_id = database["person"].aggregate([{"$sample": {"size": 1}}]).next()["_id"]


def test_get_by_id(client):
    response = client.get(f"{ENDPOINT}/{random_person_id}")

    assert response.status_code == 200


@patch("quyca.services.person_service.get_person_by_id")
def test_get_person_by_id_returns_500_on_unexpected_error(mock_service, client):
    mock_service.side_effect = Exception("boom")

    response = client.get(f"{ENDPOINT}/123")

    assert response.status_code == 500
    assert response.get_json() == {"error": "Internal server error"}


def test_get_api_person_by_id(client):
    response = client.get(f"/person/{random_person_id}")

    assert response.status_code == 200


def test_get_api_person_by_id_unknown_id_returns_404(client):
    response = client.get(f"/person/123")

    assert response.status_code == 404
    assert response.get_json() == {"error": f"The person with id 123 does not exist."}


def test_get_person_by_id_returns_every_field_by_default(client):
    full = client.get(f"{ENDPOINT}/0000000317").get_json()["data"]
    summary = client.get(f"{ENDPOINT}/0000000317?view=summary").get_json()["data"]

    assert set(summary) <= {
        "id",
        "full_name",
        "affiliations",
        "external_ids",
        "citations_count",
        "products_count",
        "h_index",
        "h5_index",
    }
    assert set(summary) < set(full)
    assert {key: full[key] for key in summary} == summary
    assert "birthdate" not in full


def test_person_with_unknown_birthdate_has_no_age():
    assert Person(_id="1", full_name=None, birthdate=-1).age is None
    assert Person(_id="1", full_name=None, birthdate=301813200).age is not None
