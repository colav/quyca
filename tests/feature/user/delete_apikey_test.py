from unittest.mock import patch, Mock
from quyca.application.routes.app.user_crud_app_router import NotEntityException


ROUTER = "application.routes.app.user_crud_app_router"
def _headers():
    return {"Authorization": "Bearer fake.jwt.token"}
def test_delete_apikey_no_token(client):
    resp = client.delete("/app/users/test@test.com/apikey")
    assert resp.status_code == 401
def test_delete_apikey_wrong_user(client):
    with patch(f"{ROUTER}.verify_jwt_in_request", return_value=True), patch(
        f"{ROUTER}.get_jwt_identity", return_value="other@test.com"
    ):
        resp = client.delete("/app/users/test@test.com/apikey", headers=_headers())
        assert resp.status_code == 403
def test_delete_apikey_user_not_found(client):
    usecase_mock = Mock()
    usecase_mock.delete_apikey.side_effect = NotEntityException("Usuario test@test.com no encontrado")

    with patch(f"{ROUTER}.verify_jwt_in_request", return_value=True), patch(
        f"{ROUTER}.get_jwt_identity", return_value="test@test.com"
    ), patch(f"{ROUTER}.usecase", usecase_mock):
        resp = client.delete("/app/users/test@test.com/apikey", headers=_headers())
        assert resp.status_code == 404
def test_delete_apikey_success(client):
    usecase_mock = Mock()
    usecase_mock.delete_apikey.return_value = {"success": True, "msg": "API key eliminada correctamente"}

    with patch(f"{ROUTER}.verify_jwt_in_request", return_value=True), patch(
        f"{ROUTER}.get_jwt_identity", return_value="test@test.com"
    ), patch(f"{ROUTER}.usecase", usecase_mock):
        resp = client.delete("/app/users/test@test.com/apikey", headers=_headers())
        assert resp.status_code == 200
        assert resp.json["success"] is True
