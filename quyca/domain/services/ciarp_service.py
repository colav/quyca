from application.usecases.process_ciarp_file import ProcessCiarpFileUseCase
from application.usecases.save_ciarp_file import SaveCiarpFileUseCase
from infrastructure.repositories.user_repository import UserRepositoryMongo


class CiarpService:
    """
    Injects use cases and user repository.
    """

    def __init__(
        self,
        process_usecase: ProcessCiarpFileUseCase,
        save_usecase: SaveCiarpFileUseCase,
        user_repo: UserRepositoryMongo,
    ):
        self.process_usecase = process_usecase
        self.save_usecase = save_usecase
        self.user_repo = user_repo

    """
    Validates token, processes file, emails report, saves file, and returns HTTP result tuple.
    """

    def handle_ciarp_upload(self, file, claims, token, upload_date):
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
            if result.get("msg", "").startswith("El archivo enviado no cumple"):
                return result, 422
            return result, 400

        file.stream.seek(0)
        save_result = self.save_usecase.execute(file, ror_id, institution, "ciarp")
        result.update({"file_msg": save_result.get("msg")})

        return result, 200
