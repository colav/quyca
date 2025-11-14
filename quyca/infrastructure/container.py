from infrastructure.repositories.pdf_repository import PDFRepository
from infrastructure.repositories.gmail_repository import GmailRepository
from infrastructure.repositories.google_drive_repository import GoogleDriveRepository
from infrastructure.repositories.file_repository import FileRepository
from infrastructure.notifications.staff_notification import StaffNotification
from application.usecases.process_staff_file import ProcessStaffFileUseCase
from application.usecases.process_ciarp_file import ProcessCiarpFileUseCase
from application.usecases.save_staff_file import SaveStaffFileUseCase
from application.usecases.save_ciarp_file import SaveCiarpFileUseCase
from domain.services.staff_report_service import StaffReportService
from domain.services.ciarp_report_service import CiarpReportService
from infrastructure.repositories.user_repository import UserRepositoryMongo

"""
DI composer for Staff: builds infrastructure, use cases and service.
"""


def build_staff_service():
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


def build_ciarp_service():
    pdf_repo = PDFRepository()
    gmail_repo = GmailRepository()
    drive_repo = GoogleDriveRepository()
    file_repo = FileRepository(drive_repo)

    report_service = CiarpReportService(pdf_repo, gmail_repo)
    notification_service = StaffNotification(gmail_repo)

    process_usecase = ProcessCiarpFileUseCase(report_service, notification_service)
    save_usecase = SaveCiarpFileUseCase(file_repo)
    user_repo = UserRepositoryMongo()

    return process_usecase, save_usecase, user_repo
