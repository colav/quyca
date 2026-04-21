from typing import Any, cast
from flask.testing import FlaskClient


def test_login_success(client: FlaskClient) -> None:
    response = client.post("/app/login", json={"email": "test@test.com", "password": "123456"})
    assert response.status_code == 200
    json_data = cast(dict[str, Any], response.get_json())
    assert json_data["success"] is True
    set_cookie = response.headers.get("Set-Cookie", "")
    assert "access_token_cookie=" in set_cookie


def test_login_fail_invalid_password(client: FlaskClient) -> None:
    response = client.post("/app/login", json={"email": "test@test.com", "password": "BADPASS"})
    assert response.status_code == 401
    json_data = cast(dict[str, Any], response.get_json())
    assert json_data["success"] is False
