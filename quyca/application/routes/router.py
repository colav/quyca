from flask import Blueprint

from quyca.application.routes.affiliation_router import affiliation_router
from quyca.application.routes.apc_router import apc_router
from quyca.application.routes.completer_router import completer_router
from quyca.application.routes.docs_router import router as docs_router
from quyca.application.routes.geo_router import geo_router
from quyca.application.routes.info_router import info_router
from quyca.application.routes.patent_router import patent_router
from quyca.application.routes.person_router import person_router
from quyca.application.routes.ping_router import ping_router
from quyca.application.routes.project_router import project_router
from quyca.application.routes.search_router import search_router
from quyca.application.routes.source_router import source_router
from quyca.application.routes.submit_router import submit_router
from quyca.application.routes.user_auth_router import user_auth_router
from quyca.application.routes.user_crud_router import user_crud_router
from quyca.application.routes.work_router import work_router
from quyca.application.routes.me_router import me_router

from quyca.config import settings

router = Blueprint("router", __name__)

router.register_blueprint(search_router, url_prefix=f"{settings.API_URL_PREFIX}/search")
router.register_blueprint(affiliation_router, url_prefix=f"{settings.API_URL_PREFIX}/affiliation")
router.register_blueprint(person_router, url_prefix=f"{settings.API_URL_PREFIX}/person")
router.register_blueprint(source_router, url_prefix=f"{settings.API_URL_PREFIX}/source")
router.register_blueprint(work_router, url_prefix=f"{settings.API_URL_PREFIX}/work")
router.register_blueprint(patent_router, url_prefix=f"{settings.API_URL_PREFIX}/patent")
router.register_blueprint(project_router, url_prefix=f"{settings.API_URL_PREFIX}/project")
router.register_blueprint(geo_router, url_prefix=f"{settings.API_URL_PREFIX}/geo")
router.register_blueprint(apc_router, url_prefix=f"{settings.API_URL_PREFIX}/apc")
router.register_blueprint(completer_router, url_prefix=f"{settings.API_URL_PREFIX}/completer")
router.register_blueprint(user_auth_router, url_prefix=f"{settings.API_URL_PREFIX}")
router.register_blueprint(me_router, url_prefix=f"{settings.API_URL_PREFIX}")
router.register_blueprint(user_crud_router, url_prefix=f"{settings.API_URL_PREFIX}")
router.register_blueprint(submit_router, url_prefix=f"{settings.API_URL_PREFIX}/submit")

router.register_blueprint(info_router, url_prefix=f"{settings.API_URL_PREFIX}")
router.register_blueprint(ping_router, url_prefix=f"{settings.API_URL_PREFIX}")
router.register_blueprint(docs_router, url_prefix=f"{settings.API_URL_PREFIX}")
