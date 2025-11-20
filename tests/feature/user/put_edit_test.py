# tests/feature/user/put_edit_test.py
from unittest.mock import Mock, patch

ROUTER_MOD = "application.routes.app.user_crud_app_router"

def _admin_headers():
    return {"Authorization": "Bearer fake.jwt.token"}

def test_edit_user_no_token(client):
    resp = client.put("/app/admin/users/x@x.com", json={"rol": "staff"})
    assert resp.status_code == 401

def test_edit_user_non_admin(client):
    with patch(f"{ROUTER_MOD}.verify_jwt_in_request", return_value=True), \
        patch(f"{ROUTER_MOD}.get_jwt", return_value={"rol": "staff"}):

        resp = client.put("/app/admin/users/x@x.com", headers=_admin_headers(), json={"rol": "staff"})
        assert resp.status_code == 403
        assert "Permiso denegado" in resp.json["msg"]

def test_edit_user_success(client):
    usecase_mock = Mock()
    usecase_mock.update_user_info.return_value = {"success": True, "msg": "Actualizado"}

    with patch(f"{ROUTER_MOD}.verify_jwt_in_request", return_value=True), \
        patch(f"{ROUTER_MOD}.get_jwt", return_value={"rol": "admin"}), \
        patch(f"{ROUTER_MOD}.usecase", usecase_mock):

        resp = client.put("/app/admin/users/x@x.com", headers=_admin_headers(), json={"rol": "staff"})
        assert resp.status_code == 200
        assert resp.json["success"] is True
