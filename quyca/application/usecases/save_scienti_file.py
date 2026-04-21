from quyca.infrastructure.repositories.file_repository import FileRepository
from werkzeug.datastructures import FileStorage
from typing import Any

"""
Use case for saving SCIENTI uploaded files.
"""


class SaveScientiFileUseCase:
    """
    Injects the file repository dependency.
    """

    def __init__(self, file_repo: FileRepository):
        self.file_repo = file_repo

    def execute(
        self,
        file: FileStorage,
        ror_id: str,
        institution: str,
    ) -> dict[str, Any]:
        """
        Saves the SCIENTI file in the corresponding storage.
        """
        result: dict[str, Any] = self.file_repo.save_file(
            file=file, ror_id=ror_id, institution=institution, file_type="scienti"
        )
        return result
