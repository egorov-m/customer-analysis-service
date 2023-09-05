from celery import Celery

from config import settings

cas_api_worker = Celery(
    "cas_worker",
    broker=settings.get_redis_worker_url(),
    backend=settings.get_redis_worker_url(),
)

cas_api_worker.conf.timezone = "UTC"

cas_api_worker.conf.update(
    result_serializer="pickle",
    accept_content=["json", "pickle"]
)
