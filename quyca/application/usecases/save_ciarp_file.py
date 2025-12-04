from typing import Dict, Any
from infrastructure.repositories.file_repository import FileRepository


class SaveCiarpFileUseCase:
    """
    Use case: persist validated CIARP file in Drive (or local fallback).
    """

    def __init__(self, file_repo: FileRepository):
        self.file_repo = file_repo

    """
    Saves file and returns repository result payload.
    """

    def execute(self, file: Any, ror_id: str, institution: str, file_type: str = "ciarp") -> Dict[str, str]:
        result: Dict[str, Any] = self.file_repo.save_file(file, ror_id, institution, file_type)
        return result
