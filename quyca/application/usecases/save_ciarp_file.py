from typing import Dict, Any
from quyca.domain.repositories.file_repository_interface import IFileRepository


class SaveCiarpFileUseCase:
    """Persists validated CIARP files in the configured storage."""

    def __init__(self, file_repo: IFileRepository):
        self.file_repo = file_repo

    def execute(self, file: Any, ror_id: str, institution: str, file_type: str = "ciarp") -> Dict[str, str]:
        """Saves the file and returns the repository response."""
        result: Dict[str, Any] = self.file_repo.save_file(file, ror_id, institution, file_type)
        return result
