import io
from unittest.mock import patch

"""
Helper function to authenticate a test user and return a valid JWT token.
"""


def get_auth_token(client):
    response = client.post("/app/login", json={"email": "test@test.com", "password": "123456"})
    assert response.status_code == 200, f"Login failed: {response.json}"
    return response.json["access_token"]


"""
Test: Upload with an invalid or expired token should return 401.
"""


def test_ciarp_upload_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token"}

    response = client.post(
        "/app/submit/ciarp",
        headers=headers,
        data={"file": (io.BytesIO(b"excel-content"), "ciarp.xlsx")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 401
    assert response.json["msg"] in ["Token inválido o expirado", "Token no encontrado en headers"]


"""
Test: Upload with invalid or missing columns should return 422.
"""


def test_ciarp_upload_with_invalid_columns(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    with patch("quyca.application.routes.app.ciarp_app_router.CiarpService.handle_ciarp_upload") as mock_service:
        mock_service.return_value = (
            {
                "success": False,
                "errores": 1,
                "duplicados": 0,
                "msg": "El archivo enviado no cumple con el formato requerido de columnas",
                "detalles": ["Columna sin nombre en posición 20"],
            },
            422,
        )

        data = {"file": (io.BytesIO(b"excel-content"), "ciarp.xlsx")}
        response = client.post("/app/submit/ciarp", headers=headers, data=data, content_type="multipart/form-data")

        assert response.status_code == 422
        assert response.json["success"] is False
        assert response.json["msg"].startswith("El archivo enviado no cumple con el formato requerido")


"""
Test: Upload an empty file should return a 400 error message.
"""


def test_ciarp_upload_empty_file(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    with patch("quyca.application.routes.app.ciarp_app_router.CiarpService.handle_ciarp_upload") as mock_service:
        mock_service.return_value = (
            {"success": False, "msg": "El archivo cargado está vacío. Verifique que contenga información."},
            400,
        )

        data = {"file": (io.BytesIO(b""), "ciarp.xlsx")}
        response = client.post("/app/submit/ciarp", headers=headers, data=data, content_type="multipart/form-data")

        assert response.status_code == 400
        assert response.json["msg"] == "El archivo cargado está vacío. Verifique que contenga información."


"""
Test: Successful CIARP file upload should return 200 and success=True.
"""


def test_ciarp_upload_success(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    with patch("quyca.application.routes.app.ciarp_app_router.CiarpService.handle_ciarp_upload") as mock_service:
        mock_service.return_value = (
            {"success": True, "errores": 0, "duplicados": 1, "pdf_base64": "JVBERi0xLjQKJ..."},
            200,
        )

        data = {"file": (io.BytesIO(b"excel-content"), "ciarp.xlsx")}
        response = client.post("/app/submit/ciarp", headers=headers, data=data, content_type="multipart/form-data")

        assert response.status_code == 200
        assert response.json["success"] is True


"""
Test: Upload request without a file should return 400 with proper message.
"""


def test_ciarp_upload_no_file(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/app/submit/ciarp", headers=headers, data={})

    assert response.status_code == 400
    assert response.json["success"] is False
    assert response.json["msg"] == "Archivo requerido"


"""
Test: Upload with validation errors should return 400 and include error count.
"""


def test_ciarp_upload_with_errors(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    with patch("quyca.application.routes.app.ciarp_app_router.CiarpService.handle_ciarp_upload") as mock_service:
        mock_service.return_value = (
            {"success": False, "errores": 3, "duplicados": 0, "pdf_base64": "JVBERi0xLjQKJ..."},
            400,
        )

        data = {"file": (io.BytesIO(b"excel-content"), "ciarp.xlsx")}
        response = client.post("/app/submit/ciarp", headers=headers, data=data, content_type="multipart/form-data")

        assert response.status_code == 400
        assert response.json["success"] is False
        assert response.json["errores"] == 3


"""
Test: Upload with duplicate records should return 200 and include duplicate count.
"""


def test_ciarp_upload_with_duplicates(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    with patch("quyca.application.routes.app.ciarp_app_router.CiarpService.handle_ciarp_upload") as mock_service:
        mock_service.return_value = (
            {"success": True, "errores": 0, "duplicados": 2, "pdf_base64": "JVBERi0xLjQKJ..."},
            200,
        )

        data = {"file": (io.BytesIO(b"excel-with-duplicates"), "ciarp.xlsx")}
        response = client.post("/app/submit/ciarp", headers=headers, data=data, content_type="multipart/form-data")

        assert response.status_code == 200
        assert response.json["duplicados"] == 2


"""
Test: Simulate email failure during report sending; should return 500.
"""


def test_ciarp_upload_email_failed(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    with patch("quyca.application.routes.app.ciarp_app_router.CiarpService.handle_ciarp_upload") as mock_service:
        mock_service.return_value = ({"success": False, "msg": "Fallo al enviar correo"}, 500)

        data = {"file": (io.BytesIO(b"excel-content"), "ciarp.xlsx")}
        response = client.post("/app/submit/ciarp", headers=headers, data=data, content_type="multipart/form-data")

        assert response.status_code == 500
        assert response.json["success"] is False
