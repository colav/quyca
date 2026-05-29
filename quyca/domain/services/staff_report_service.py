from typing import Any

import pandas as pd
from quyca.domain.models.staff_report_model import StaffReport
from quyca.domain.repositories.dataframe_annotator_interface import IDataFrameAnnotator
from quyca.domain.repositories.pdf_repository_interface import IPDFRepository
from quyca.domain.repositories.xlsx_exporter_interface import IXlsxExporter
from quyca.domain.validators.staff_validator import StaffValidator


class StaffReportService:
    """Generates validation reports for Staff data."""

    def __init__(
        self,
        pdf_repo: IPDFRepository,
        annotator: IDataFrameAnnotator,
        xlsx_exporter: IXlsxExporter,
    ):
        self.pdf_repo = pdf_repo
        self.annotator = annotator
        self.xlsx_exporter = xlsx_exporter

    def generate_report(
        self,
        df: pd.DataFrame,
        institution: str,
        filename: str,
        upload_date: str,
        user: str,
        normalized_changes: list[dict[str, Any]] | None = None,
    ) -> tuple[StaffReport, list[dict]]:
        """Validates the dataframe and generates Staff report attachments."""
        staff_report: StaffReport = StaffValidator.validate_dataframe(df)

        attachments: list[dict] = []
        annotated_df = self.annotator.annotate(df, staff_report)
        excel_bytes = self.xlsx_exporter.to_excel_bytes(annotated_df)

        attachments.append(
            {
                "bytes": excel_bytes,
                "filename": "staff_validado.xlsx",
                "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
        )

        has_normalizations = bool(normalized_changes)
        if (
            staff_report.total_errors > 0
            or len(staff_report.warnings) > 0
            or staff_report.total_duplicates > 0
            or has_normalizations
        ):
            pdf_bytes = self.pdf_repo.generate_quality_report(
                staff_report.grouped_errors,
                staff_report.grouped_warnings,
                staff_report.duplicates,
                institution,
                filename,
                upload_date,
                user,
                normalized_changes=normalized_changes,
            )

            attachments.insert(0, {"bytes": pdf_bytes, "filename": "reporte_staff.pdf", "mime": "application/pdf"})

        return staff_report, attachments
