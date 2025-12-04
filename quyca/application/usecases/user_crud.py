from typing import Any, Optional, List, cast
from domain.services.user_service import UserCrudService
from infrastructure.repositories.user_crud_repository import UserCrudRepository
from infrastructure.notifications.staff_notification import StaffNotification
from infrastructure.repositories.gmail_repository import GmailRepository


class UserCrudUseCase:
    def __init__(self) -> None:
        self.repo = UserCrudRepository()
        self.service: Optional[UserCrudService] = None

    def _ensure_service(self) -> UserCrudService:
        if self.service is None:
            gmail_repo = GmailRepository()
            notifier = StaffNotification(gmail_repo)
            self.service = UserCrudService(self.repo, notifier)

        return self.service

    def create_user(
        self, email: str, institution: str, ror_id: str, rol: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        service = self._ensure_service()
        return cast(dict[str, Any], service.create_user(email, institution, ror_id, rol, raw_payload=payload))

    def get_all_users(self) -> List[dict[str, Any]]:
        service = self._ensure_service()
        return cast(List[dict[str, Any]], service.get_all_users())

    def deactivate_user(self, email: str) -> dict[str, Any]:
        service = self._ensure_service()
        return cast(dict[str, Any], service.deactivate_user(email))

    def activate_user(self, email: str) -> dict[str, Any]:
        service = self._ensure_service()
        return cast(dict[str, Any], service.activate_user(email))

    def update_password(self, email: str) -> dict[str, Any]:
        service = self._ensure_service()
        return cast(dict[str, Any], service.update_password(email))

    def update_user_info(self, old_email: str, new_email: str, new_rol: str, payload: dict[str, Any]) -> dict[str, Any]:
        service = self._ensure_service()
        return cast(dict[str, Any], service.update_user_info(old_email, new_email, new_rol, raw_payload=payload))

    def create_or_regenerate_apikey(self, email: str, expires: int | None) -> dict[str, Any]:
        service = self._ensure_service()
        return cast(dict[str, Any], service.regenerate_apikey(email, expires))

    def update_apikey_expiration(self, email: str, expires: int | None) -> dict[str, Any]:
        service = self._ensure_service()
        return cast(dict[str, Any], service.update_apikey_expiration(email, expires))

    def delete_apikey(self, email: str) -> dict[str, Any]:
        service = self._ensure_service()
        return cast(dict[str, Any], service.delete_apikey(email))
