from typing import Dict
from infrastructure.repositories.file_repository import FileRepository


class SaveStaffFileUseCase:
    def __init__(self, file_repo: FileRepository):
        self.file_repo = file_repo

    """Saves the uploaded file into Google Drive for the corresponding institution"""

    def execute(self, file, ror_id: str, institution: str, file_type: str = "staff") -> Dict[str, str]:
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

        return self.file_repo.save_file(file, ror_id, institution, file_type)
