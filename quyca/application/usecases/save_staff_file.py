from typing import Any, Dict
from infrastructure.repositories.file_repository import FileRepository
from werkzeug.datastructures import FileStorage


class SaveStaffFileUseCase:
    """
    Use case: persist validated Staff file in Drive (or local fallback).
    """

    def __init__(self, file_repo: FileRepository):
        self.file_repo = file_repo

    """
    Saves file and returns repository result payload.
    """

    def execute(self, file: FileStorage, ror_id: str, institution: str, file_type: str = "staff") -> dict[str, Any]:
        if not hasattr(file, "save"):
            raise TypeError("El objeto 'file' debe ser un FileStorage compatible.")
        if not ror_id:
            raise ValueError("ror_id es requerido")
        if not institution:
            raise ValueError("institution es requerida")

        try:
            if hasattr(file, "seek"):
                file.seek(0)
            elif hasattr(getattr(file, "stream", None), "seek"):
                file.stream.seek(0)
        except Exception:
            pass

        result: Dict[str, Any] = self.file_repo.save_file(file, ror_id, institution, file_type)
        return result
