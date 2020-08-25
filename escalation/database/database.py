# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

import os

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from flask_sqlalchemy import SQLAlchemy

from app_deploy_data.app_settings import DATABASE_CONFIG

try:
    from app_deploy_data.models import *
    from app_deploy_data.models import Base
except ModuleNotFoundError:
    raise (ModuleNotFoundError, "models.py file not defined- run database setup")


db = SQLAlchemy()

runtime_defined_db_url = os.environ.get("DATABASE_URL")
if runtime_defined_db_url:
    engine = create_engine(runtime_defined_db_url)
    print(f"Using runtime-defined db url {runtime_defined_db_url}")
else:
    url = URL(**DATABASE_CONFIG)
    engine = create_engine(URL(**DATABASE_CONFIG), convert_unicode=True)
    print(f"Using config-defined db url {url}")


db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# allows us to use the table_class.query instead of db.session.query(table_class)
Base.query = db_session.query_property()
