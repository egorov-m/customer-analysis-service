from typing import Generator

from sqlmodel import Session

from cas_worker.db.database import get_session


def get_db() -> Generator:
    try:
        session: Session = get_session()
        with session.begin() as transaction:
            yield session
    finally:
        session.close()
