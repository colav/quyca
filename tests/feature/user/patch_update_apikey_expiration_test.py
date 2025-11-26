from unittest.mock import patch, Mock
from quyca.application.routes.app.user_crud_app_router import NotEntityException

ROUTER = "application.routes.app.user_crud_app_router"

def _headers():
    return {"Authorization": "Bearer fake.jwt.token"}


def test_update_apikey_exp_no_token(client):
    resp = client.patch("/app/users/test@test.com/apikey")
    assert resp.status_code == 401


def test_update_apikey_exp_wrong_user(client):
    with patch(f"{ROUTER}.verify_jwt_in_request", return_value=True), \
        patch(f"{ROUTER}.get_jwt_identity", return_value="other@test.com"):

        resp = client.patch("/app/users/test@test.com/apikey",
            json={"expires": 9999999999},
            headers=_headers()
        )

        assert resp.status_code == 403


def test_update_apikey_exp_invalid_timestamp(client):
    usecase_mock = Mock()
    usecase_mock.update_apikey_expiration.side_effect = NotEntityException(
        "La ficha de expiración debe ser futura"
    )

    with patch(f"{ROUTER}.verify_jwt_in_request", return_value=True), \
        patch(f"{ROUTER}.get_jwt_identity", return_value="test@test.com"), \
        patch(f"{ROUTER}.usecase", usecase_mock):

        resp = client.patch("/app/users/test@test.com/apikey",
            json={"expires": 100},
            headers=_headers()
        )

        assert resp.status_code == 400


def test_update_apikey_exp_success(client):
    usecase_mock = Mock()
    usecase_mock.update_apikey_expiration.return_value = {
        "success": True,
        "msg": "Expiración del API key actualizada"
    }

    with patch(f"{ROUTER}.verify_jwt_in_request", return_value=True), \
        patch(f"{ROUTER}.get_jwt_identity", return_value="test@test.com"), \
        patch(f"{ROUTER}.usecase", usecase_mock):

        resp = client.patch("/app/users/test@test.com/apikey",
                            json={"expires": 1900000000},
                            headers=_headers())

        assert resp.status_code == 200
        assert resp.json["success"] is True