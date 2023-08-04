from pydantic import UUID4

from cas_shared.schemas.base import TunedModel


class CasTask(TunedModel):
    task_id: UUID4
    task_status: str
