from unittest.mock import Mock, patch

ROUTER_MOD = "application.routes.app.user_crud_app_router"

def _admin_headers():
    return {"Authorization": "Bearer fake.jwt.token"}

def test_list_users_no_token(client):
    resp = client.get("/app/admin/users")
    assert resp.status_code == 401
    assert "Token" in resp.json["msg"]

def test_list_users_non_admin(client):
    with patch(f"{ROUTER_MOD}.verify_jwt_in_request", return_value=True), patch(
        f"{ROUTER_MOD}.get_jwt", return_value={"rol": "staff"}):
        resp = client.get("/app/admin/users", headers=_admin_headers())
        assert resp.status_code == 403
        assert "Permiso" in resp.json["msg"]

def test_list_users_success(client):
    usecase_mock = Mock()
    usecase_mock.get_all_users.return_value = [{"email": "a@a.com", "rol": "staff"}]
    with patch(f"{ROUTER_MOD}.verify_jwt_in_request", return_value=True), patch(
        f"{ROUTER_MOD}.get_jwt", return_value={"rol": "admin"}
    ), patch(f"{ROUTER_MOD}.usecase", usecase_mock):
        resp = client.get("/app/admin/users", headers=_admin_headers())
        assert resp.status_code == 200
        assert resp.json["success"] is True
        assert isinstance(resp.json["data"], list)
