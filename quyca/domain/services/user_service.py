import string, random, time
from typing import List, Any
from quyca.domain.models.user_model import User
from quyca.infrastructure.security.password_hasher import hash_password
from quyca.domain.repositories.user_crud_repository_interface import IUserCrudRepository
from quyca.domain.exceptions.not_entity_exception import NotEntityException
from quyca.infrastructure.notifications.notification import StaffNotification

"""
Application service for admin user management (create, list, toggle, reset, edit).
"""


class UserCrudService:
    """Application service for administrative user management."""

    def __init__(self, user_repo: IUserCrudRepository, notifier: StaffNotification) -> None:
        self.user_repo = user_repo
        self.notifier = notifier

    def _generate_password(self, length: int = 10) -> str:
        """Generates a random alphanumeric password."""
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for _ in range(length))

    def _generate_apikey_id(self, length: int = 10) -> str:
        """Generates a random API key identifier."""
        chars = string.ascii_letters + string.digits
        return "".join(random.choice(chars) for _ in range(length))

    def _validate_create_user_payload(self, payload: dict[str, Any]) -> None:
        """Validates required fields for user creation."""
        required = {"institution", "ror_id", "role"}
        received = set(payload.keys())

        missing = required - received
        extra = received - required

        if missing or extra:
            msg_parts = []
            if missing:
                msg_parts.append("Faltan: " + ",".join(sorted(missing)))
            if extra:
                msg_parts.append("Sobran: " + ", ".join(sorted(extra)))
            raise NotEntityException(" | ".join(msg_parts))

    def _validate_edit_user_payload(self, payload: dict[str, Any]) -> None:
        """Validates fields allowed for user editing."""
        allowed = {"email", "role"}
        received = set(payload.keys())

        if not received:
            raise NotEntityException("Debes enviar al menos email o role.")

        extra = received - allowed

        if extra:
            raise NotEntityException("Sobran: " + ", ".join(sorted(extra)))

    def _validate_apikey_expiration(self, expires: int | None) -> None:
        """Validates API key expiration timestamp."""
        if expires is None:
            return

        if not isinstance(expires, int):
            raise NotEntityException("El campo 'expires' debe ser un timestamp entero o None")

        current = int(time.time())

        if expires <= current:
            raise NotEntityException("La fecha de expiración debe ser futura")

        if expires - current < 86400:
            raise NotEntityException("La expiración mínima del API key es de 1 día")

    def create_user(
        self, email: str, institution: str, ror_id: str, role: str, raw_payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Creates a new user and sends credentials via email."""
        if raw_payload is None:
            raise NotEntityException("Payload requerido: institution, ror_id y role.")

        self._validate_create_user_payload(raw_payload)

        if role.lower() == "admin":
            raise NotEntityException("No se pueden crear usuarios con el role 'admin'.")

        existing_by_ror = self.user_repo.find_by_ror_id(ror_id)
        if existing_by_ror:
            return {
                "success": False,
                "msg": (
                    f"Para la institución: {existing_by_ror.institution} ya existe un correo registrado: "
                    f"{existing_by_ror.email}. Si deseas asignar un nuevo correo, edita el usuario existente."
                ),
            }

        raw_password = self._generate_password()
        hashe_password = hash_password(raw_password)

        user = User(
            id=ror_id,
            email=email.strip().lower(),
            password=hashe_password,
            institution=institution.strip(),
            role=role.strip(),
            is_active=True,
            apikey=None,
        )

        self.user_repo.create(user)

        subject = "Tu cuenta en la plataforma ImpactU ha sido creada exitosamente."

        self.notifier.send_custom_email(subject, role, institution, email, raw_password, ror_id=ror_id)

        return {
            "success": True,
            "msg": f"Usuario {email} Creado exitosamente y contraseña enviada por correo electrónico.",
        }

    def get_all_users(self) -> List[dict[str, Any]]:
        """Lists users excluding admins and sensitive fields."""
        users = self.user_repo.get_all()
        filtered_users = [u for u in users if u.role.lower() != "admin"]
        return [
            {"email": u.email, "institution": u.institution, "id": u.id, "role": u.role, "is_active": u.is_active}
            for u in filtered_users
        ]

    def deactivate_user(self, email: str) -> dict[str, Any]:
        """Disables a user account by setting its 'is_active' flag to False."""
        self.user_repo.deactivate(email)
        return {"success": True, "msg": f"El usuario {email} ha sido desactivado."}

    def activate_user(self, email: str) -> dict[str, Any]:
        """Reactivates a user account by setting its 'is_active' flag to True."""
        self.user_repo.activate(email)
        return {"success": True, "msg": f"El usuario {email} ha sido activado."}

    def update_password(self, email: str) -> dict[str, Any]:
        """Resets password, stores hash, and emails the new credentials."""

        all_users = self.user_repo.get_all()
        user = next((u for u in all_users if u.email == email), None)

        if not user:
            raise NotEntityException(f"El usuario con correo {email} no fue encontrado")

        if not user.is_active:
            raise NotEntityException(f"Cuenta desactivada para el usuario {email}")

        new_password = self._generate_password()
        hashed = hash_password(new_password)

        self.user_repo.update_password(email, hashed)

        subject = "Tu contraseña ha sido restablecida"

        self.notifier.send_email_change_password(
            email=email, subject=subject, password=new_password, institution=user.institution, ror_id=user.id
        )
        return {"success": True, "msg": f"La contraseña de {email} se actualizó correctamente."}

    def update_user_info(
        self, old_email: str, new_email: str, new_role: str, raw_payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Edits email and/or role, blocks admin role and admin account edits, and reissues credentials on email change."""
        self._validate_edit_user_payload(raw_payload)

        if new_role and new_role.strip().lower() == "admin":
            return {"success": False, "msg": "No se puede asignar el rol 'admin' a un usuario."}
        current_user = self.user_repo.get_all()
        current = next((u for u in current_user if u.email == old_email), None)
        if not current:
            return {"success": False, "msg": f"Usuario con correo {old_email} no encontrado."}

        if not current.is_active:
            raise NotEntityException(f"Cuenta desactivada para el usuario {old_email}")

        if current.role.strip().lower() == "admin":
            return {"success": False, "msg": "No se pueden editar los datos de este usuario"}

        correo_cambiado = old_email.strip().lower() != new_email.strip().lower()
        role_cambiado = bool(new_role) and new_role.strip().lower() != current.role.strip().lower()

        if not correo_cambiado and not role_cambiado:
            return {"success": False, "msg": "No se detectaron cambios para actualizar."}

        updated_user = self.user_repo.update_user_info(old_email, new_email, new_role)
        if not updated_user:
            raise NotEntityException(f"Usuario con correo {old_email} no encontrado.")

        if role_cambiado and not correo_cambiado:
            return {"success": True, "msg": f"Rol del usuario {old_email} actualizado correctamente."}

        if correo_cambiado:
            new_password = self._generate_password()
            hashed = hash_password(new_password)

            self.user_repo.update_password(updated_user.email, hashed)

            subject = "Tu cuenta en la plataforma ImpactU ha sido creada exitosamente."
            self.notifier.send_custom_email(
                subject=subject,
                role=updated_user.role,
                institution=updated_user.institution,
                email=updated_user.email,
                password=new_password,
                ror_id=updated_user.id,
            )

            msg = (
                f"Correo del usuario actualizado correctamente y notificación enviada a {new_email}."
                if not role_cambiado
                else f"Correo y rol del usuario actualizados correctamente. Notificación enviada a {new_email}."
            )

            return {"success": True, "msg": msg}

        return {"success": True, "msg": "Usuario actualizado correctamente."}

    def regenerate_apikey(self, email: str, expires: int | None) -> dict[str, Any]:
        """
        Generates a new API key for the user, after validating expiration rules,
        and stores it in the database.
        """
        self._validate_apikey_expiration(expires)

        new_key = {"id": self._generate_apikey_id(), "expires": expires}
        self.user_repo.regenerate_apikey(email, new_key)
        return {"success": True, "apikey": new_key}

    def update_apikey_expiration(self, email: str, expires: int | None) -> dict[str, Any]:
        """
        Updates the expiration timestamp of the user's API key after validating
        that the timestamp is valid.
        """
        self._validate_apikey_expiration(expires)

        self.user_repo.update_apikey_expiration(email, expires)
        return {"success": True, "msg": "Expiración del API key actualizada"}

    def delete_apikey(self, email: str) -> dict[str, Any]:
        """Removes the user's API key by setting it to None."""
        self.user_repo.delete_apikey(email)
        return {"success": True, "msg": "API key eliminada correctamente"}
