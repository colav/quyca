import io

import pandas as pd

from quyca.domain.models.staff_report_model import StaffReport
from quyca.domain.repositories.dataframe_annotator_interface import IDataFrameAnnotator
from quyca.domain.repositories.pdf_repository_interface import IPDFRepository
from quyca.domain.repositories.xlsx_exporter_interface import IXlsxExporter
from quyca.domain.validators.ciarp_validator import CiarpValidator


class CiarpReportService:
    """Generates validation reports for CIARP data."""

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
        self, df: pd.DataFrame, institution: str, filename: str, upload_date: str, user: str
    ) -> tuple[StaffReport, list[dict]]:
        """Validates the dataframe and generates CIARP report attachments."""
        ciarp_report: StaffReport = CiarpValidator.validate_dataframe(df)

        attachments = []
        pdf_bytes: io.BytesIO | None = None

        if ciarp_report.total_errors > 0 or len(ciarp_report.warnings) > 0 or ciarp_report.total_duplicates > 0:
            advertencias_resumen = {"total_advertencias": len(ciarp_report.warnings)}

            pdf_bytes = self.pdf_repo.generate_quality_report_ciarp(
                ciarp_report.grouped_errors,
                advertencias_resumen,
                ciarp_report.duplicates,
                institution,
                filename,
                upload_date,
                user,
            )

            attachments = [{"bytes": pdf_bytes, "filename": "reporte_ciarp.pdf", "mime": "application/pdf"}]

            annotated_df = self.annotator.annotate(df, ciarp_report)
            excel_bytes = self.xlsx_exporter.to_excel_bytes(annotated_df)
            attachments.append(
                {
                    "bytes": excel_bytes,
                    "filename": "ciarp_validado.xlsx",
                    "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                }
            )

        return ciarp_report, attachments
