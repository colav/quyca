from pytest import fixture
from typing import Generator
from flask import Flask
from flask.testing import FlaskClient
from quyca.app import create_app


@fixture()
def app() -> Generator[Flask, None, None]:
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "JWT_TOKEN_LOCATION": ["cookies"],
            "JWT_ACCESS_COOKIE_NAME": "access_token_cookie",
            "JWT_COOKIE_SECURE": False,
            "JWT_COOKIE_SAMESITE": "Lax",
            "JWT_COOKIE_DOMAIN": None,
            "JWT_COOKIE_CSRF_PROTECT": False,
            "JWT_CSRF_IN_COOKIES": False,
        }
    )

    yield app


@fixture()
def client(app: Flask) -> Generator[FlaskClient, None, None]:
    client = app.test_client()

    yield client
