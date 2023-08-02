from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine

from config import settings

engine = create_engine(
    settings.get_postgres_url(),
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW
)

get_session: sessionmaker = sessionmaker(engine)
