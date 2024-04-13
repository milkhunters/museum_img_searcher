import urllib.parse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


def create_psql_session(
        username: str,
        password: str,
        host: str,
        port: int,
        database: str,
        echo: bool = False,
) -> tuple:
    engine = create_engine(
        "postgresql://{username}:{password}@{host}:{port}/{database}".format(
            username=urllib.parse.quote_plus(username),
            password=urllib.parse.quote_plus(password),
            host=host,
            port=port,
            database=database
        ),
        echo=echo,
    )
    return engine, sessionmaker(bind=engine)


Base = declarative_base()
