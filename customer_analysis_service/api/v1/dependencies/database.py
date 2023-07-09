from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from customer_analysis_service.config import Config
from customer_analysis_service.db.database import create_engine, get_session_maker, Database

cas_config: Config = Config.load_config()
engine = create_engine(url=cas_config.dbPostgres.get_url())
pool: sessionmaker = get_session_maker(engine)


def get_db():
    session: Session = pool()
    return Database(session)
