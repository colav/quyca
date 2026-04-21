from elasticsearch import Elasticsearch, __version__ as es_version

from quyca.config import settings

es_database: Elasticsearch | None = None
if es_version[0] < 8:
    es_database = Elasticsearch(settings.ES_SERVER, http_auth=(settings.ES_USERNAME, settings.ES_PASSWORD))
else:
    es_database = Elasticsearch(settings.ES_SERVER, basic_auth=(settings.ES_USERNAME, settings.ES_PASSWORD))
