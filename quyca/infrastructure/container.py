from typing import Tuple
from infrastructure.repositories.pdf_repository import PDFRepository
from infrastructure.repositories.gmail_repository import GmailRepository
from infrastructure.repositories.google_drive_repository import GoogleDriveRepository
from infrastructure.repositories.file_repository import FileRepository
from infrastructure.notifications.staff_notification import StaffNotification
from application.usecases.process_staff_file import ProcessStaffFileUseCase
from application.usecases.save_staff_file import SaveStaffFileUseCase
from domain.services.staff_report_service import StaffReportService
from infrastructure.repositories.user_repository import UserRepositoryMongo


def build_staff_service() -> Tuple[ProcessStaffFileUseCase, SaveStaffFileUseCase, UserRepositoryMongo]:
    pdf_repo = PDFRepository()
    gmail_repo = GmailRepository()
    drive_repo = GoogleDriveRepository()
    file_repo = FileRepository(drive_repo)

    report_service = StaffReportService(pdf_repo, gmail_repo)
    notification_service = StaffNotification(gmail_repo)

    process_usecase = ProcessStaffFileUseCase(report_service, notification_service)
    save_usecase = SaveStaffFileUseCase(file_repo)
    user_repo = UserRepositoryMongo()

    return process_usecase, save_usecase, user_repo
