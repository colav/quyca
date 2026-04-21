from __future__ import annotations

from typing import Any

from quyca.application.usecases.process_ciarp_file import ProcessCiarpFileUseCase
from quyca.application.usecases.save_ciarp_file import SaveCiarpFileUseCase


class CiarpService:
    """
    Injects use cases and user repository.
    """

    def __init__(
        self,
        process_usecase: ProcessCiarpFileUseCase,
        save_usecase: SaveCiarpFileUseCase,
    ):
        self.process_usecase = process_usecase
        self.save_usecase = save_usecase

    """
    Validates token, processes file, emails report, saves file, and returns HTTP result tuple.
    """

    def handle_ciarp_upload(self, file: Any, claims: dict[str, Any], upload_date: str) -> tuple[dict[str, Any], int]:
        email = claims.get("sub")
        ror_id = claims.get("_id")
        institution = claims.get("institution")
        user = claims.get("role")

        if (
            not isinstance(email, str)
            or not isinstance(ror_id, str)
            or not isinstance(institution, str)
            or not isinstance(user, str)
            or not email
            or not ror_id
            or not institution
            or not user
        ):
            return {"success": False, "msg": "Token inválido o revocado"}, 401

        if not file:
            return {"success": False, "msg": "Archivo requerido"}, 400

        result = self.process_usecase.execute(file, institution, file.filename, upload_date, user, email, ror_id)
        if not result["success"]:
            if result.get("msg", "").startswith("El archivo enviado no cumple"):
                return result, 422
            return result, 400

        file.stream.seek(0)
        save_result = self.save_usecase.execute(file, ror_id, institution, "ciarp")
        result.update({"file_msg": save_result.get("msg")})

        return result, 200
