import io
import os
import base64

import pandas as pd

from quyca.domain.models.staff_report_model import StaffReport
from quyca.domain.normalizers.staff_normalizer_service import StaffNormalizerService
from quyca.domain.services.staff_report_service import StaffReportService
from quyca.domain.validators.error_grouper import ErrorGrouper
from quyca.domain.validators.staff_validator import REQUIRED_COLUMNS, StaffValidator
from quyca.infrastructure.notifications.notification import StaffNotification


class ProcessStaffFileUseCase:
    """
    Use case: validate, normalize, report and notify for Staff Excel uploads.

    Flow:
        1. Read Excel.
        2. Structural cleaning (always).
        3. Semantic mapping (always, before validation).
        4. Column validation  → if invalid: PDF + email + return.
        5. Empty file guard.
        6. Row validation     → generate PDF + email.
        7. If no errors: expose normalized df and changelog for saving.
        8. Return result with pdf_base64 and changelog.
    """

    def __init__(
        self,
        report_service: StaffReportService,
        notification_service: StaffNotification,
        normalizer: StaffNormalizerService | None = None,
    ):
        self.report_service = report_service
        self.notification_service = notification_service
        self.normalizer = normalizer or StaffNormalizerService()

    def execute(
        self,
        file: io.BytesIO,
        institution: str,
        filename: str,
        upload_date: str,
        user: str,
        email: str,
        ror_id: str,
    ) -> dict:
        """Validates the file, generates reports, sends notifications and returns the result."""

        # 1. Extension check
        extension = os.path.splitext(filename)[1].lower()
        if extension != ".xlsx":
            return {
                "success": False,
                "msg": f"Formato de archivo no permitido ({extension}). Solo se admiten archivos .xlsx.",
            }

        try:
            df = pd.read_excel(file, engine="openpyxl")
        except Exception as e:
            return {"success": False, "msg": f"Error al leer el archivo Excel: {str(e)}"}

        df_original = df.copy()

        # 2. Structural cleaning — always, before any validation
        df = self.normalizer.clean(df)

        # 3. Semantic mapping — always, so validators see canonical values
        df, changelog = self.normalizer.map_values(df)
        normalized_unique_values_count = len(
            {
                (
                    str(change.get("columna", "")),
                    str(change.get("valor_original", "")),
                    str(change.get("valor_normalizado", "")),
                )
                for change in changelog
            }
        )

        normalized_df = df[[col for col in REQUIRED_COLUMNS if col in df.columns]].copy()

        # 4. Column validation
        valid, errores_columnas, _ = StaffValidator.validate_columns(df)
        if not valid:
            column_errors = [
                {
                    "fila": 1,
                    "columna": "columnas",
                    "detalle": err,
                    "valor": "",
                }
                for err in errores_columnas
            ]

            staff_report = StaffReport(
                total_errors=len(errores_columnas),
                total_duplicates=0,
                errors=column_errors,
                grouped_errors=ErrorGrouper.group_errors(column_errors),
                warnings=[],
                grouped_warnings=[],
                duplicates=[],
            )

            pdf_bytes = self.report_service.pdf_repo.generate_quality_report(
                staff_report.grouped_errors, [], [], institution, filename, upload_date, user
            )

            annotated_df = self.report_service.annotator.annotate(df, staff_report)
            excel_bytes = self.report_service.xlsx_exporter.to_excel_bytes(annotated_df)

            attachments = [
                {"bytes": pdf_bytes, "filename": "reporte_staff.pdf", "mime": "application/pdf"},
                {
                    "bytes": excel_bytes,
                    "filename": "staff_validado.xlsx",
                    "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                },
            ]

            self.notification_service.send_report(
                staff_report, institution, filename, upload_date, user, email, "Staff", attachments, ror_id
            )

            pdf_bytes.seek(0)
            return {
                "success": False,
                "errors": staff_report.total_errors,
                "duplicates": 0,
                "msg": "El archivo enviado no cumple con el formato requerido de columnas",
                "details": errores_columnas,
                "pdf_base64": base64.b64encode(pdf_bytes.read()).decode(),
            }

        # 5. Empty file guard
        if df.empty or df.dropna(how="all").empty:
            return {"success": False, "msg": "El archivo cargado está vacío. Verifique que contenga información."}

        # 6. Row-level validation
        staff_report, attachments = self.report_service.generate_report(
            df,
            institution,
            filename,
            upload_date,
            user,
            normalized_changes=changelog,
        )

        self.notification_service.send_report(
            staff_report, institution, filename, upload_date, user, email, "Staff", attachments, ror_id
        )

        pdf_base64 = None
        for att in attachments:
            if att["filename"].endswith(".pdf"):
                pdf_base64 = base64.b64encode(att["bytes"].read()).decode()
                break

        result = {
            "success": staff_report.total_errors == 0,
            "errors": staff_report.total_errors,
            "warnings": len(staff_report.warnings),
            "duplicates": staff_report.total_duplicates,
            "pdf_base64": pdf_base64,
            "normalized_unique_values_count": normalized_unique_values_count,
        }

        # 7. Expose normalized df for saving — only when no errors
        if staff_report.total_errors == 0:
            result["df_original"] = df_original
            result["df_normalized"] = normalized_df  # required-schema only, consumed by StaffService

        return result
