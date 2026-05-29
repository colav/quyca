from __future__ import annotations

import os
import io
import base64
from typing import Any, Dict, Optional

import pandas as pd

from quyca.domain.models.staff_report_model import StaffReport
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

        pdf_base64: Optional[str] = None

        valid, errors_columns, _ = self.validator.validate_columns(df)
        if not valid:
            column_errors = [
                {"field": "columnas", "msg": err, "index": None, "index_excel": None} for err in errors_columns
            ]
            grouped_errors = [{"field": "columnas", "errors": column_errors}]

            report = StaffReport(
                total_errors=len(errors_columns),
                total_duplicates=0,
                errors=column_errors,
                grouped_errors=grouped_errors,
                warnings=[],
                grouped_warnings=[],
                duplicates=[],
            )

            pdf_bytes = self.report_service.pdf_repo.generate_quality_report(
                grouped_errors, [], [], institution, filename, upload_date, user
            )
            attachments = [{"bytes": pdf_bytes, "filename": "reporte_ciarp.pdf", "mime": "application/pdf"}]

            self.notification_service.send_report(
                report, institution, filename, upload_date, user, email, "Ciarp", attachments, ror_id
            )

            pdf_bytes.seek(0)
            pdf_base64 = base64.b64encode(pdf_bytes.read()).decode()

            return {
                "success": False,
                "errors": report.total_errors,
                "duplicates": 0,
                "msg": "El archivo enviado no cumple con el formato requerido de columnas",
                "details": errors_columns,
                "pdf_base64": pdf_base64,
            }

        report, attachments = self.report_service.generate_report(df, institution, filename, upload_date, user)

        self.notification_service.send_report(
            report, institution, filename, upload_date, user, email, "Ciarp", attachments, ror_id
        )

        for att in attachments:
            att_filename = att.get("filename")
            if isinstance(att_filename, str) and att_filename.endswith(".pdf"):
                bytes_obj = att.get("bytes")
                if isinstance(bytes_obj, io.BytesIO):
                    bytes_obj.seek(0)
                    pdf_base64 = base64.b64encode(bytes_obj.read()).decode()
                    break

        return {
            "success": report.total_errors == 0,
            "errors": report.total_errors,
            "warnings": len(report.warnings),
            "duplicates": report.total_duplicates,
            "pdf_base64": pdf_base64,
        }
