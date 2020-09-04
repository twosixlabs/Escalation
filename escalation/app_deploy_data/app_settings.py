# todo: move this to config json
import os

if not os.environ.get("DATABASE_CONFIG"):
    DATABASE_CONFIG = {
        "drivername": "postgresql+psycopg2",
        "host": "postgres_db",
        "port": "5432",
        "username": "escalation",
        "password": "escalation_pwd",
        "database": "escalation",
    }
else:
    from sqlalchemy.engine.url import make_url

    url = make_url(os.environ.get("DATABASE_CONFIG"))
    DATABASE_CONFIG = {
        "drivername": url.drivername,
        "host": url.host,
        "port": url.port,
        "username": url.username,
        "password": url.password,
        "database": url.database,
    }
