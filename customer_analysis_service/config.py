from dataclasses import dataclass

from environs import Env


@dataclass
class DbPostgresConfig:
    """Postgres database connection variables"""

    db_name: str
    db_host: str
    db_port: str
    db_user: str
    db_password: str

    driver: str = "psycopg2"
    database_system: str = "postgresql"

    def get_url(self) -> str:
        return f"{self.database_system}+{self.driver}://{self.db_user}:{self.db_password}@{self.db_host}/{self.db_name}"


@dataclass
class Config:
    """All in one configuration's class"""

    dbPostgres: DbPostgresConfig

    @classmethod
    def load_config(cls, path: str | None = None):
        env: Env = Env()
        env.read_env(path)

        return Config(dbPostgres=DbPostgresConfig(db_name=env('POSTGRES_DB'),
                                                  db_host=env('POSTGRES_HOST'),
                                                  db_port=env('POSTGRES_PORT'),
                                                  db_user=env('POSTGRES_USER'),
                                                  db_password=env('POSTGRES_PASSWORD')))
