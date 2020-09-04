This directory contains configuration jsons and a models.py file that define the app.

`main_config.json` Defines the layout of the Escalation dashboard

Each other panel of the dashboard gets its own configuration json.

`models.py` is generated automatically using the sqlalchemy code generator library `sqlacodegen`, and defines in Python the tables that exist in the linked database. 