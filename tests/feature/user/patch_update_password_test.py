from unittest.mock import Mock, patch

ROUTER_MOD = "application.routes.app.user_crud_app_router"


def _admin_headers():
    return {"Authorization": "Bearer fake.jwt.token"}


def test_update_password_no_token(client):
    resp = client.patch("/app/admin/users/x@x.com")
    assert resp.status_code == 401


def test_update_password_non_admin(client):
    with patch(f"{ROUTER_MOD}.verify_jwt_in_request", return_value=True), patch(
        f"{ROUTER_MOD}.get_jwt", return_value={"rol": "staff"}
    ):

        resp = client.patch("/app/admin/users/x@x.com", headers=_admin_headers())
        assert resp.status_code == 403


def test_update_password_success(client):
    usecase_mock = Mock()
    usecase_mock.update_password.return_value = {"success": True, "msg": "Contraseña actualizada"}

    with patch(f"{ROUTER_MOD}.verify_jwt_in_request", return_value=True), patch(
        f"{ROUTER_MOD}.get_jwt", return_value={"rol": "admin"}
    ), patch(f"{ROUTER_MOD}.usecase", usecase_mock):

        resp = client.patch("/app/admin/users/x@x.com", headers=_admin_headers())
        assert resp.status_code == 200
        assert resp.json["success"] is True
