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


@dataclass(frozen=True)
class StaffUploadResult:
    """
    Data structure representing the result of a Staff upload operation.

    Attributes:
        payload (dict): Result payload returned to the client.
        error (Optional[StaffUploadError]): Semantic error type if the
        operation failed, otherwise None.
    """

    payload: dict
    error: Optional[StaffUploadError] = None


class StaffService:
    """
    Application service responsible for orchestrating the Staff upload flow.

    This service coordinates authentication validation, file processing,
    validation execution and final persistence of the uploaded Staff file.
    """

    def __init__(
        self,
        process_usecase: ProcessStaffFileUseCase,
        save_usecase: SaveStaffFileUseCase,
    ):
        self.process_usecase = process_usecase
        self.save_usecase = save_usecase

    def handle_staff_upload(self, file: FileStorage, claims: dict[str, Any], upload_date: str) -> StaffUploadResult:
        """
        Handles the Staff file upload process.

        Validates the JWT claims, checks the uploaded file, executes the
        processing use case, and if successful, persists the file using
        the save use case.
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

        result = self.process_usecase.execute(
            file_bytes,
            institution,
            filename,
            upload_date,
            user,
            email,
            ror_id,
        )

        if not result["success"]:
            msg = str(result.get("msg", ""))
            if msg.startswith("El archivo enviado no cumple con el formato requerido de columnas"):
                return StaffUploadResult(result, StaffUploadError.UNPROCESSABLE_ENTITY)
            return StaffUploadResult(result, StaffUploadError.BAD_REQUEST)

        file.stream.seek(0)
        save_result = self.save_usecase.execute(file, ror_id, institution)

        result.update({"file_msg": save_result.get("msg")})

        return StaffUploadResult(result, None)
