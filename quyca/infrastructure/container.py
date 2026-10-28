from quyca.application.usecases.get_me import GetMeUseCase
from quyca.application.usecases.login_user import LoginUserUseCase

from quyca.infrastructure.auth.flask_cookie_reader import FlaskJwtCookieReader
from quyca.infrastructure.auth.flask_jwt_verifier import FlaskJwtVerifier
from quyca.infrastructure.security.jwt_token_service import JwtTokenService
from quyca.infrastructure.repositories.user_repository import UserRepositoryMongo


def build_login_usecase() -> LoginUserUseCase:
    """Build login use case."""
    return LoginUserUseCase(user_repo=UserRepositoryMongo(), token_service=JwtTokenService())


def build_get_me_usecase() -> GetMeUseCase:
    """Build get-me use case."""
    return GetMeUseCase(
        cookie_reader=FlaskJwtCookieReader(),
        jwt_verifier=FlaskJwtVerifier(),
    )
