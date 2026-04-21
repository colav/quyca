from typing import Tuple

from quyca.application.usecases.get_me import GetMeUseCase
from quyca.application.usecases.login_user import LoginUserUseCase
from quyca.application.usecases.save_staff_file import SaveStaffFileUseCase
from quyca.application.usecases.save_ciarp_file import SaveCiarpFileUseCase
from quyca.application.usecases.save_scienti_file import SaveScientiFileUseCase
from quyca.application.usecases.process_staff_file import ProcessStaffFileUseCase
from quyca.application.usecases.process_ciarp_file import ProcessCiarpFileUseCase

from quyca.infrastructure.auth.flask_cookie_reader import FlaskJwtCookieReader
from quyca.infrastructure.auth.flask_jwt_verifier import FlaskJwtVerifier
from quyca.infrastructure.security.jwt_token_service import JwtTokenService
from quyca.infrastructure.repositories.pdf_repository import PDFRepository
from quyca.infrastructure.repositories.gmail_repository import GmailRepository
from quyca.infrastructure.repositories.google_drive_repository import GoogleDriveRepository
from quyca.infrastructure.repositories.file_repository import FileRepository
from quyca.infrastructure.repositories.excel_cleaner_openpyxl import ExcelCleanerOpenpyxl
from quyca.infrastructure.notifications.notification import StaffNotification
from quyca.infrastructure.repositories.user_repository import UserRepositoryMongo
from quyca.infrastructure.annotators.annotator import Annotator
from quyca.infrastructure.exporters.xlsx_writer_exporter import XlsxWriteExporter

from quyca.domain.services.scienti_service import ScientiService
from quyca.domain.services.staff_report_service import StaffReportService
from quyca.domain.services.ciarp_report_service import CiarpReportService

"""
DI composer for Staff: builds infrastructure, use cases and service.
"""

"""
Builds and wires dependencies for the Staff service.
"""


def build_staff_service() -> Tuple[ProcessStaffFileUseCase, SaveStaffFileUseCase]:
    """Build Staff upload use cases."""
    pdf_repo = PDFRepository()
    gmail_repo = GmailRepository()
    drive_repo = GoogleDriveRepository()
    excel_cleaner = ExcelCleanerOpenpyxl()
    file_repo = FileRepository(drive_repo, excel_cleaner)

    report_service = StaffReportService(pdf_repo, Annotator(), XlsxWriteExporter())
    notification_service = StaffNotification(gmail_repo)

    process_usecase = ProcessStaffFileUseCase(report_service, notification_service)
    save_usecase = SaveStaffFileUseCase(file_repo)

    return process_usecase, save_usecase


def build_ciarp_service() -> Tuple[ProcessCiarpFileUseCase, SaveCiarpFileUseCase]:
    """Build CIARP upload use cases."""
    pdf_repo = PDFRepository()
    gmail_repo = GmailRepository()
    drive_repo = GoogleDriveRepository()
    excel_cleaner = ExcelCleanerOpenpyxl()
    file_repo = FileRepository(drive_repo, excel_cleaner)

    report_service = CiarpReportService(pdf_repo, Annotator(), XlsxWriteExporter())
    notification_service = StaffNotification(gmail_repo)

    process_usecase = ProcessCiarpFileUseCase(report_service, notification_service)
    save_usecase = SaveCiarpFileUseCase(file_repo)

    return process_usecase, save_usecase


def build_scienti_service() -> ScientiService:
    """Build Scienti service dependencies."""
    gmail_repo = GmailRepository()
    drive_repo = GoogleDriveRepository()
    excel_cleaner = ExcelCleanerOpenpyxl()
    file_repo = FileRepository(drive_repo, excel_cleaner)

    notification = StaffNotification(gmail_repo)
    save_usecase = SaveScientiFileUseCase(file_repo)

    return ScientiService(notification=notification, save_usecase=save_usecase)


def build_login_usecase() -> LoginUserUseCase:
    """Build login use case."""
    return LoginUserUseCase(user_repo=UserRepositoryMongo(), token_service=JwtTokenService())


def build_get_me_usecase() -> GetMeUseCase:
    """Build get-me use case."""
    return GetMeUseCase(
        cookie_reader=FlaskJwtCookieReader(),
        jwt_verifier=FlaskJwtVerifier(),
    )


def build_file_repository() -> FileRepository:
    """Build file repository with Drive and cleaner."""
    drive_repo = GoogleDriveRepository()
    cleaner = ExcelCleanerOpenpyxl()
    return FileRepository(drive_repo=drive_repo, excel_cleaner=cleaner)
