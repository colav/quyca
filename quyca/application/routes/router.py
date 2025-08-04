from flask import Blueprint

from application.routes.api.apc_api_router import apc_api_router
from application.routes.app.info_app_router import info_app_router
from config import settings
from application.routes.app.patent_app_router import patent_app_router
from application.routes.app.project_app_router import project_app_router
from application.routes.app.search_app_router import search_app_router
from application.routes.api.search_api_router import search_api_router
from application.routes.app.affiliation_app_router import affiliation_app_router
from application.routes.api.affiliation_api_router import affiliation_api_router
from application.routes.app.person_app_router import person_app_router
from application.routes.api.person_api_router import person_api_router
from application.routes.app.work_app_router import work_app_router
from application.routes.docs_router import router as docs_router
from application.routes.ping_router import ping_router

from application.routes.app.completer_app_router import completer_app_router

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import settings

limiter = Limiter(get_remote_address, default_limits=settings.API_LIMITS)

limiter.limit(settings.API_LIMITS)(person_api_router)
limiter.limit(settings.API_LIMITS)(search_api_router)
limiter.limit(settings.API_LIMITS)(affiliation_api_router)
limiter.limit(settings.API_LIMITS)(apc_api_router)
limiter.limit(settings.API_LIMITS)(ping_router)
limiter.limit(settings.API_LIMITS)(docs_router)

router = Blueprint("router", __name__)

router.register_blueprint(ping_router)
router.register_blueprint(docs_router)

router.register_blueprint(info_app_router, url_prefix=f"{settings.APP_URL_PREFIX}")

router.register_blueprint(search_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/search")
router.register_blueprint(search_api_router, url_prefix=f"{settings.API_URL_PREFIX}/search")

router.register_blueprint(affiliation_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/affiliation")
router.register_blueprint(affiliation_api_router, url_prefix=f"{settings.API_URL_PREFIX}/affiliation")

router.register_blueprint(person_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/person")
router.register_blueprint(person_api_router, url_prefix=f"{settings.API_URL_PREFIX}/person")

router.register_blueprint(work_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/work")

router.register_blueprint(patent_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/patent")

router.register_blueprint(project_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/project")

router.register_blueprint(apc_api_router, url_prefix=f"{settings.API_URL_PREFIX}/apc")

router.register_blueprint(completer_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/completer")
