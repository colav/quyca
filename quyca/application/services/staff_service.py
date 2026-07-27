from __future__ import annotations

import io
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from werkzeug.datastructures import FileStorage

from quyca.application.usecases.process_staff_file import ProcessStaffFileUseCase
from quyca.application.usecases.save_staff_file import SaveStaffFileUseCase


class StaffUploadError(Enum):
    """
    Enumeration representing semantic upload errors.

    These errors are interpreted by the router layer and translated
    into the corresponding HTTP responses.
    """

    UNAUTHORIZED = "unauthorized"
    BAD_REQUEST = "bad_request"
    UNPROCESSABLE_ENTITY = "unprocessable_entity"
    INTERNAL_ERROR = "internal_error"


@dataclass(frozen=True)
class StaffUploadResult:
    """Result object returned by `StaffService.handle_staff_upload`.

    Attributes:
        payload: A serializable dictionary with the API response payload.
        error: Optional semantic error from `StaffUploadError` that the
            router layer will map to an HTTP response code.
    """

    payload: dict
    error: Optional[StaffUploadError] = None


class StaffService:
    """
    Application service responsible for orchestrating the Staff upload flow.
    """

    def __init__(
        self,
        process_usecase: ProcessStaffFileUseCase,
        save_usecase: SaveStaffFileUseCase,
    ):
        self.process_usecase = process_usecase
        self.save_usecase = save_usecase

    def handle_staff_upload(self, file: FileStorage, claims: dict[str, Any], upload_date: str) -> StaffUploadResult:
        """Handle a staff Excel upload end-to-end.

        Validates token claims, reads and processes the incoming Excel file
        via the `ProcessStaffFileUseCase`, and persists original and
        normalized files via the `SaveStaffFileUseCase` when processing
        succeeds. Returns a `StaffUploadResult` containing the response
        payload and an optional semantic error used by the router.

        Args:
            file: Incoming uploaded file (Werkzeug `FileStorage`).
            claims: JWT claims extracted from the request token.
            upload_date: ISO date string representing the upload time.

        Returns:
            StaffUploadResult: payload and optional `StaffUploadError`.
        """
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
            return StaffUploadResult(
                {"success": False, "msg": "Token inválido o revocado"},
                StaffUploadError.UNAUTHORIZED,
            )

        if not file:
            return StaffUploadResult(
                {"success": False, "msg": "Archivo requerido"},
                StaffUploadError.BAD_REQUEST,
            )

        filename = file.filename or ""
        if not filename:
            return StaffUploadResult(
                {"success": False, "msg": "Archivo requerido"},
                StaffUploadError.BAD_REQUEST,
            )

        file.stream.seek(0)
        file_bytes = io.BytesIO(file.stream.read())
        file_bytes.seek(0)

        result = self.process_usecase.execute(file_bytes, institution, filename, upload_date, user, email, ror_id)

        if not result["success"]:
            msg = str(result.get("msg", ""))
            if msg.startswith("El archivo enviado no cumple con el formato requerido de columnas"):
                return StaffUploadResult(result, StaffUploadError.UNPROCESSABLE_ENTITY)
            return StaffUploadResult(result, StaffUploadError.BAD_REQUEST)

        # Only reached when success=True (no errors)
        df_original = result.pop("df_original", None)
        df_normalized = result.pop("df_normalized", None)

        if df_normalized is not None:
            if df_original is None:
                df_original = df_normalized

            save_result = self.save_usecase.execute(
                ror_id=ror_id,
                institution=institution,
                original_filename=filename,
                df_original=df_original,
                df_normalized=df_normalized,
            )
            result["file_msg"] = save_result.get("msg_normalized")

            if not save_result.get("success", False):
                result["success"] = False
                result["msg"] = (
                    save_result.get("msg_normalized")
                    or save_result.get("msg_original")
                    or ("Error al guardar el archivo")
                )
                return StaffUploadResult(result, StaffUploadError.INTERNAL_ERROR)

            # Raw changelog is internal-only and should not be exposed by the API.
            result.pop("changelog", None)

        return StaffUploadResult(result, None)
