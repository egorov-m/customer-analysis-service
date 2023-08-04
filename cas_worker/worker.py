from celery import Celery

from cas_worker.tests.visualizer.group import GroupVisualizerQuantity
from config import settings


cas_worker = Celery(
    "cas_worker",
    broker=settings.get_redis_url(),
    backend=settings.get_redis_url(),
    include=["cas_worker.tests"]
)
cas_worker.register_task(GroupVisualizerQuantity())

cas_worker.conf.timezone = "UTC"

cas_worker.conf.update(
    # task_serializer="pickle",
    result_serializer="pickle",
    accept_content=["json", "pickle"]
)
