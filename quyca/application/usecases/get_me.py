from dataclasses import dataclass
from typing import Any

from quyca.domain.auth.session_status import SessionStatus
from quyca.domain.auth.auth_ports import IJwtCookieReader, IJwtVerifier


@dataclass(frozen=True)
class MeResult:
    """Represents the result of the session status query."""

    status: SessionStatus
    msg: str
    user: dict[str, Any] | None = None


class GetMeUseCase:
    """Use case that checks the current authenticated session."""

    def __init__(
        self,
        cookie_reader: IJwtCookieReader,
        jwt_verifier: IJwtVerifier,
    ) -> None:
        self.cookie_reader = cookie_reader
        self.jwt_verifier = jwt_verifier

    def execute(self) -> MeResult:
        """Returns the current session status and user info if valid."""
        token = self.cookie_reader.get_access_token()
        if not token:
            return MeResult(SessionStatus.SESION_NO_INICIADA, "Sesión no iniciada")

        claims = self.jwt_verifier.verify_from_cookies()
        if not claims:
            return MeResult(SessionStatus.TOKEN_EXPIRADO, "Token expirado o inválido")

        email = claims.get("sub")
        if not isinstance(email, str) or not email.strip():
            return MeResult(SessionStatus.TOKEN_EXPIRADO, "Token revocado o inválido")

        return MeResult(
            SessionStatus.SESION_ACTIVA,
            "Sesión activa",
            user={
                "_id": claims.get("_id"),
                "institution": claims.get("institution"),
                "role": claims.get("role"),
                "email": email,
            },
        )
