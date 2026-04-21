import os
import io
import base64
import pandas as pd
from quyca.domain.validators.staff_validator import StaffValidator
from quyca.domain.services.staff_report_service import StaffReportService
from quyca.infrastructure.notifications.notification import StaffNotification


class ProcessStaffFileUseCase:
    """
    Use case: validate, report and notify for Staff Excel uploads.
    """

    def __init__(self, report_service: StaffReportService, notification_service: StaffNotification):
        self.report_service = report_service
        self.notification_service = notification_service

    def execute(
        self, file: io.BytesIO, institution: str, filename: str, upload_date: str, user: str, email: str, ror_id: str
    ) -> dict:
        """Validates the file, generates reports, sends notifications and returns the result."""
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
        valid, errores_columnas, _ = StaffValidator.validate_columns(df)
        if not valid:
            return {
                "success": False,
                "errors": len(errores_columnas),
                "duplicates": 0,
                "msg": "El archivo enviado no cumple con el formato requerido de columnas",
                "details": errores_columnas,
            }

        if df.empty or df.dropna(how="all").empty:
            return {"success": False, "msg": "El archivo cargado está vacío. Verifique que contenga información."}

        staff_report, attachments = self.report_service.generate_report(df, institution, filename, upload_date, user)

        self.notification_service.send_report(
            staff_report, institution, filename, upload_date, user, email, "Staff", attachments, ror_id
        )

        pdf_base64 = None
        for att in attachments:
            if att["filename"].endswith(".pdf"):
                pdf_base64 = base64.b64encode(att["bytes"].read()).decode()
                break

        return {
            "success": staff_report.total_errors == 0,
            "errors": staff_report.total_errors,
            "warnings": len(staff_report.warnings),
            "duplicates": staff_report.total_duplicates,
            "pdf_base64": pdf_base64,
        }
