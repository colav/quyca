import io
import pandas as pd
from domain.models.staff_report_model import StaffReport
from domain.validators.ciarp_validator import CiarpValidator
from domain.repositories.pdf_repository_interface import IPDFRepository
from infrastructure.repositories.gmail_repository import GmailRepository
from infrastructure.exporters.xlsx_writer_exporter import XlsxWriteExporter
from quyca.infrastructure.annotators.annotator import Annotator


class CiarpReportService:
    """Generates PDF + Excel reports for CIARP validation results."""

    def __init__(self, pdf_repo: IPDFRepository, gmail_repo: GmailRepository | None = None):
        self.pdf_repo = pdf_repo
        self.gmail_repo = gmail_repo

    def generate_report(
        self, df: pd.DataFrame, institution: str, filename: str, upload_date: str, user: str
    ) -> tuple[StaffReport, list[dict]]:
        ciarp_report: StaffReport = CiarpValidator.validate_dataframe(df)

        attachments = []
        pdf_bytes: io.BytesIO | None = None

        if ciarp_report.total_errores > 0 or len(ciarp_report.advertencias) > 0 or ciarp_report.total_duplicados > 0:
            advertencias_resumen = {"total_advertencias": len(ciarp_report.advertencias)}

            pdf_bytes = self.pdf_repo.generate_quality_report_ciarp(
                ciarp_report.errores_agrupados,
                advertencias_resumen,
                ciarp_report.duplicados,
                institution,
                filename,
                upload_date,
                user,
            )

            attachments = [{"bytes": pdf_bytes, "filename": "reporte_ciarp.pdf", "mime": "application/pdf"}]

            annotated_df = Annotator.annotate(df, ciarp_report)
            excel_bytes = XlsxWriteExporter.to_excel_bytes(annotated_df)
            attachments.append(
                {
                    "bytes": excel_bytes,
                    "filename": "ciarp_validado.xlsx",
                    "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                }
            )

        return ciarp_report, attachments
