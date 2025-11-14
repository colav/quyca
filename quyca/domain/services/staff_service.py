from typing import Any
from application.usecases.process_staff_file import ProcessStaffFileUseCase
from application.usecases.save_staff_file import SaveStaffFileUseCase
from infrastructure.repositories.user_repository import UserRepositoryMongo
from werkzeug.datastructures import FileStorage

"""Validates a users JWT token and returns the associated data (ror_id, institution)"""


class StaffService:
    def __init__(
        self,
        process_usecase: ProcessStaffFileUseCase,
        save_usecase: SaveStaffFileUseCase,
        user_repo: UserRepositoryMongo,
    ):
        self.process_usecase = process_usecase
        self.save_usecase = save_usecase
        self.user_repo = user_repo

    def handle_staff_upload(
        self, file: FileStorage, claims: dict[str, Any], token: str, upload_date: str
    ) -> tuple[dict, int]:
        email = claims.get("sub")
        ror_id = claims.get("ror_id")
        institution = claims.get("institution")
        user = claims.get("rol")

        if not self.user_repo.is_token_valid(email, token):
            return {"success": False, "msg": "Token inválido o revocado"}, 401

        if not file:
            return {"success": False, "msg": "Archivo requerido"}, 400

        result = self.process_usecase.execute(file, institution, file.filename, upload_date, user, email)

        if not result["success"]:
            if result.get("msg", "").startswith("El archivo enviado no cumple con el formato requerido de columnas"):
                return result, 422
            return result, 400

        file.stream.seek(0)
        save_result = self.save_usecase.execute(file, ror_id, institution)

        result.update({"file_msg": save_result.get("msg")})

        return result, 200
