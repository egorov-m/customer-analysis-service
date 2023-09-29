from celery import Task
from sqlmodel import Session

from cas_shared.db.database import get_session


class TaskWithDbSession(Task):
    def __init__(self):
        self.session = None

    def before_start(self, task_id, args, kwargs):
        session: Session = get_session()
        with session.begin() as transaction:
            self.session = session

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        self.session.close()
