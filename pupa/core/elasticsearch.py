import pyelasticsearch

from pupa import settings


elasticsearch = None
if settings.ENABLE_ELASTICSEARCH:
    elasticsearch = pyelasticsearch.ElasticSearch(
        urls='http://{}'.format(settings.ELASTICSEARCH_HOST),
        timeout=settings.ELASTICSEARCH_TIMEOUT)
