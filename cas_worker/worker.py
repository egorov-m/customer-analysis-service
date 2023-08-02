from celery import Celery

from config import settings


celery = Celery(
    "cas_worker",
    broker=settings.get_redis_url(),
    backend=settings.get_redis_url(),
    include=["cas_worker.services"]
)

celery.conf.timezone = "UTC"
