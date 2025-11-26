from unittest.mock import patch, Mock

ROUTER = "application.routes.app.user_crud_app_router"


def _headers():
    return {"Authorization": "Bearer fake.jwt.token"}


def test_regenerate_apikey_unauthorized(client):
    """Should return 401 when no token is provided."""
    resp = client.post("/app/users/test@test.com/apikey")
    assert resp.status_code == 401


def test_regenerate_apikey_wrong_user(client):
    """Should return 403 when token identity does not match URL email."""

    with patch(f"{ROUTER}.verify_jwt_in_request", return_value=True), patch(
        f"{ROUTER}.get_jwt_identity", return_value="other@email.com"
    ):

        resp = client.post("/app/users/test@test.com/apikey", headers=_headers())
        assert resp.status_code == 403
        assert resp.json["success"] is False


def test_regenerate_apikey_success(client):
    """Should regenerate API key correctly."""

    usecase_mock = Mock()
    usecase_mock.create_or_regenerate_apikey.return_value = {
        "success": True,
        "apikey": {"id": "XYZ123", "expires": None},
    }

    with patch(f"{ROUTER}.verify_jwt_in_request", return_value=True), patch(
        f"{ROUTER}.get_jwt_identity", return_value="test@test.com"
    ), patch(f"{ROUTER}.usecase", usecase_mock):

        resp = client.post("/app/users/test@test.com/apikey", json={"expires": None}, headers=_headers())

        assert resp.status_code == 200
        assert resp.json["success"] is True
        assert "apikey" in resp.json
