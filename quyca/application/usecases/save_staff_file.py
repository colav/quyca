import io
import os
from typing import Any

import pandas as pd
from werkzeug.datastructures import FileStorage

from quyca.infrastructure.repositories.file_repository import FileRepository


class SaveStaffFileUseCase:
    """
    Use case: persist validated Staff files in Drive (or local fallback).

    When the file has no errors, saves both:
      - df_original   → file_type="staff_original"  (traceability)
      - df_normalized → file_type="staff"            (ETL)

    When the file has errors, nothing is saved.
    """

    def __init__(self, file_repo: FileRepository):
        self.file_repo = file_repo

    def execute(
        self,
        ror_id: str,
        institution: str,
        original_filename: str,
        df_original: pd.DataFrame,
        df_normalized: pd.DataFrame,
    ) -> dict[str, Any]:
        if not ror_id:
            raise ValueError("ror_id es requerido")
        if not institution:
            raise ValueError("institution es requerida")

        result_original = self.file_repo.save_file(
            self._to_filestorage(df_original, original_filename),
            ror_id,
            institution,
            file_type="staff",
            filename_prefix="ORIGINAL_",
        )

        result_normalized = self.file_repo.save_file(
            self._to_filestorage(df_normalized, original_filename),
            ror_id,
            institution,
            file_type="staff",
        )

        return {
            "success": result_original.get("success") and result_normalized.get("success"),
            "msg_original": result_original.get("msg"),
            "msg_normalized": result_normalized.get("msg"),
        }

    @staticmethod
    def _to_filestorage(df: pd.DataFrame, filename: str) -> FileStorage:
        """
        Converts a DataFrame to a FileStorage writing to a temp file first,
        so FileStorage.save() reads from a real file-backed stream.
        """
        df_to_save = df.copy()
        artifact_cols = [
            col
            for col in df_to_save.columns
            if str(col).strip().lower().startswith("unnamed") or str(col).strip().lower() == "index"
        ]
        if artifact_cols:
            df_to_save = df_to_save.drop(columns=artifact_cols)

        tmp_path = f"/tmp/_staff_fs_{os.getpid()}_{filename}"
        try:
            df_to_save.to_excel(tmp_path, index=False, engine="openpyxl")
            with open(tmp_path, "rb") as f:
                data = f.read()
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        buffer = io.BytesIO(data)
        buffer.seek(0)
        return FileStorage(
            stream=buffer,
            filename=filename,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
