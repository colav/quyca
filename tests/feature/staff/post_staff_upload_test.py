import io
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

import flask
from flask.testing import FlaskClient
from werkzeug.datastructures import FileStorage

from quyca.application.services.staff_service import StaffUploadError, StaffUploadResult


def auth_cookie(client: FlaskClient) -> None:
    """
    Crea un JWT real (con flask_jwt_extended) y lo deja en la cookie HttpOnly
    sin pasar por /app/login (que ya NO retorna access_token en JSON).
    """
    from flask_jwt_extended import create_access_token

    with client.application.app_context():
        token = create_access_token(
            identity="test@test.com",
            additional_claims={"_id": "u1", "institution": "TestInstitution", "role": "admin"},
        )

    # En Flask test client esta firma funciona: (key, value)
    client.set_cookie("access_token_cookie", token)


def test_staff_upload_invalid_token(client: FlaskClient) -> None:
    client.set_cookie("access_token_cookie", "invalid_token")

    response = client.post(
        "/app/submit/staff",
        data={"file": (io.BytesIO(b"excel-content"), "staff.xlsx")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 401
    json_data = cast(dict[str, Any], response.json)
    assert json_data["msg"] == "Token inválido o expirado"


def test_staff_upload_with_invalid_columns(client: FlaskClient) -> None:
    auth_cookie(client)

    with patch("quyca.application.routes.app.staff_app_router.StaffService.handle_staff_upload") as mock_service:
        mock_service.return_value = StaffUploadResult(
            {
                "success": False,
                "errors": 1,
                "duplicates": 0,
                "msg": "El archivo enviado no cumple con el formato requerido de columnas",
                "details": ["Columna sin nombre en posición 20"],
            },
            StaffUploadError.UNPROCESSABLE_ENTITY,
        )

        response = client.post(
            "/app/submit/staff",
            data={"file": (io.BytesIO(b"excel-content"), "staff.xlsx")},
            content_type="multipart/form-data",
        )

    assert response.status_code == 422
    json_data = cast(dict[str, Any], response.json)
    assert json_data["success"] is False
    assert json_data["msg"].startswith("El archivo enviado no cumple con el formato requerido")


def test_staff_upload_empty_file(client: FlaskClient) -> None:
    auth_cookie(client)

    with patch("quyca.application.routes.app.staff_app_router.StaffService.handle_staff_upload") as mock_service:
        mock_service.return_value = StaffUploadResult(
            {"success": False, "msg": "El archivo cargado está vacío. Verifique que contenga información."},
            StaffUploadError.BAD_REQUEST,
        )

        response = client.post(
            "/app/submit/staff",
            data={"file": (io.BytesIO(b""), "staff.xlsx")},
            content_type="multipart/form-data",
        )

    assert response.status_code == 400
    json_data = cast(dict[str, Any], response.json)
    assert json_data["msg"] == "El archivo cargado está vacío. Verifique que contenga información."


def test_staff_upload_success(client: FlaskClient) -> None:
    auth_cookie(client)

    with patch("quyca.application.routes.app.staff_app_router.StaffService.handle_staff_upload") as mock_service:
        mock_service.return_value = StaffUploadResult(
            {"success": True, "errors": 0, "duplicates": 1, "pdf_base64": "JVBERi0xLjQKJ..."},
            None,
        )

        response = client.post(
            "/app/submit/staff",
            data={"file": (io.BytesIO(b"excel-content"), "staff.xlsx")},
            content_type="multipart/form-data",
        )

    assert response.status_code == 200
    json_data = cast(dict[str, Any], response.json)
    assert json_data["success"] is True


def test_staff_upload_no_file(client: FlaskClient) -> None:
    auth_cookie(client)

    response = client.post("/app/submit/staff", data={})

    assert response.status_code == 400
    json_data = cast(dict[str, Any], response.json)
    assert json_data["success"] is False
    assert json_data["msg"] == "Archivo requerido"


def test_staff_upload_with_errors(client: FlaskClient) -> None:
    auth_cookie(client)

    with patch("quyca.application.routes.app.staff_app_router.StaffService.handle_staff_upload") as mock_service:
        mock_service.return_value = StaffUploadResult(
            {"success": False, "errors": 3, "duplicates": 0, "pdf_base64": "JVBERi0xLjQKJ..."},
            StaffUploadError.BAD_REQUEST,
        )

        response = client.post(
            "/app/submit/staff",
            data={"file": (io.BytesIO(b"excel-content"), "staff.xlsx")},
            content_type="multipart/form-data",
        )

    assert response.status_code == 400
    json_data = cast(dict[str, Any], response.json)
    assert json_data["success"] is False
    assert json_data["errors"] == 3


def test_staff_upload_with_duplicates(client: FlaskClient) -> None:
    auth_cookie(client)

    with patch("quyca.application.routes.app.staff_app_router.StaffService.handle_staff_upload") as mock_service:
        mock_service.return_value = StaffUploadResult(
            {"success": True, "errors": 0, "duplicates": 2, "pdf_base64": "JVBERi0xLjQKJ..."},
            None,
        )

        response = client.post(
            "/app/submit/staff",
            data={"file": (io.BytesIO(b"excel-with-duplicates"), "staff.xlsx")},
            content_type="multipart/form-data",
        )

    assert response.status_code == 200
    json_data = cast(dict[str, Any], response.json)
    assert json_data["duplicates"] == 2


def test_staff_upload_email_failed(client: FlaskClient) -> None:
    auth_cookie(client)

    with patch("quyca.application.routes.app.staff_app_router.StaffService.handle_staff_upload") as mock_service:
        mock_service.side_effect = Exception("Email service down")

        response = client.post(
            "/app/submit/staff",
            data={"file": (io.BytesIO(b"excel-content"), "staff.xlsx")},
            content_type="multipart/form-data",
        )

    assert response.status_code == 500
    json_data = cast(dict[str, Any], response.json)
    assert json_data["success"] is False
    assert json_data["msg"] == "Error interno del servidor"


def test_file_repository_fallback_local(tmp_path: Path) -> None:
    from quyca.infrastructure.repositories.file_repository import FileRepository

    class DummyDriveRepo:
        def get_or_create_folder(self, *args: Any, **kwargs: Any) -> str:
            raise Exception("Drive unavailable")

        def upload_file(self, *args: Any, **kwargs: Any) -> str:
            raise Exception("Drive unavailable")

    file_repo = FileRepository(cast(Any, DummyDriveRepo()))

    dummy_file = FileStorage(
        stream=io.BytesIO(b"test content"),
        filename="dummy.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    app = flask.Flask(__name__)
    app.config["LOCAL_STORAGE_PATH"] = str(tmp_path)

    with app.app_context():
        result = file_repo.save_file(dummy_file, "123", "TestInstitution", "staff")

    assert result["success"] is True
    assert "almacenamiento local" in result["msg"]

    files = list(tmp_path.rglob("*"))
    assert any("staff" in str(f) for f in files)
