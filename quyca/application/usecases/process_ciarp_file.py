from __future__ import annotations

import os
import io
import base64
from typing import Any, Dict, Optional

import pandas as pd

from quyca.domain.services.ciarp_report_service import CiarpReportService
from quyca.domain.repositories.notification_service_interface import INotificationService
from quyca.domain.validators.ciarp_validator_interface import ICiarpValidator
from quyca.domain.validators.ciarp_validator import CiarpValidator


class ProcessCiarpFileUseCase:
    """
    Use case: validate, report and notify for CIARP Excel uploads.
    """

    def __init__(
        self,
        report_service: CiarpReportService,
        notification_service: INotificationService,
        validator: ICiarpValidator = CiarpValidator,
    ):
        self.report_service = report_service
        self.notification_service = notification_service
        self.validator = validator

    def execute(
        self, file: io.BytesIO, institution: str, filename: str, upload_date: str, user: str, email: str, ror_id: str
    ) -> Dict[str, Any]:
        """Validates the file, generates the CIARP report and sends notifications."""
        extension = os.path.splitext(filename)[1].lower()
        if extension != ".xlsx":
            return {
                "success": False,
                "msg": f"Formato de archivo no permitido ({extension}). Solo se admiten archivos .xlsx.",
            }
        try:
            df = pd.read_excel(file, engine="openpyxl")
        except Exception as e:
            return {
                "success": False,
                "msg": f"Error al leer el archivo Excel: {str(e)}",
            }
        valid, errors_columns, _ = self.validator.validate_columns(df)
        if not valid:
            return {
                "success": False,
                "msg": "El archivo enviado no cumple con el formato requerido de columnas",
                "details": errors_columns,
            }

        report, attachments = self.report_service.generate_report(df, institution, filename, upload_date, user)

        self.notification_service.send_report(
            report, institution, filename, upload_date, user, email, "Ciarp", attachments, ror_id
        )

        pdf_base64: Optional[str] = None
        for att in attachments:
            if att["filename"].endswith(".pdf"):
                pdf_base64 = base64.b64encode(att["bytes"].read()).decode()
                break

        return {
            "success": report.total_errors == 0,
            "errors": report.total_errors,
            "warnings": len(report.warnings),
            "duplicates": report.total_duplicates,
            "pdf_base64": pdf_base64,
        }
