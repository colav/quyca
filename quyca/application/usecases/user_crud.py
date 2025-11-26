from domain.services.user_service import UserCrudService
from infrastructure.repositories.user_crud_repository import UserCrudRepository
from infrastructure.notifications.staff_notification import StaffNotification
from infrastructure.repositories.gmail_repository import GmailRepository

"""
Use case façade for admin user operations (wires infra to services).
"""

class UserCrudUseCase:
    def __init__(self):
        """Lazy-wires service and its dependencies."""
        self.repo = UserCrudRepository()
        self.service = None
        
    def _ensure_service(self):
        """Creates the service with Gmail notifier on first use."""
        if self.service is None:
            gmail_repo = GmailRepository()
            notifier = StaffNotification(gmail_repo)
            self.service = UserCrudService(self.repo, notifier)

    def create_user(self, email: str, institution: str, ror_id: str, rol: str, payload: dict) -> dict:
        """Delegates user creation to the service."""
        self._ensure_service()
        return self.service.create_user(email, institution, ror_id, rol, raw_payload=payload)

    def get_all_users(self) -> list[dict]:
        """Delegates users listing to the service."""
        self._ensure_service()
        return self.service.get_all_users()

    def deactivate_user(self, email: str) -> dict:
        self._ensure_service()
        return self.service.deactivate_user(email)


    def activate_user(self, email: str) -> dict:
        """Delegates user activation request to domain service."""
        self._ensure_service()
        return self.service.activate_user(email)

    def update_password(self, email: str) -> dict:
        """Delegates password reset to the service."""
        self._ensure_service()
        return self.service.update_password(email)
    
    def update_user_info(self, old_email: str, new_email: str, new_rol: str, payload: dict) -> dict:
        """Delegates email/role edition to the service."""
        self._ensure_service()
        return self.service.update_user_info(old_email, new_email, new_rol, raw_payload=payload)
    
    def create_or_regenerate_apikey(self, email: str, expires: int | None):
        """Delegates API key creation or regeneration to domain service."""
        self._ensure_service()
        return self.service.regenerate_apikey(email, expires)
    
    def update_apikey_expiration(self, email: str, expires: int | None):
        """Delegates API key expiration update to domain service."""
        self._ensure_service()
        return self.service.update_apikey_expiration(email, expires)
    
    def delete_apikey(self, email: str):
        """Delegates API key deletion to domain service."""
        self._ensure_service()
        return self.service.delete_apikey(email)