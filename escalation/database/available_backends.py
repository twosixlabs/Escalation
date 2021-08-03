from database.elasticsearch_schema import ElasticSearchConfigInterfaceBuilder
from database.sql_schema import SqlConfigInterfaceBuilder
from utility.constants import POSTGRES, ELASTICSEARCH

AVAILABLE_BACKEND_SCHEMAS = {
    POSTGRES: SqlConfigInterfaceBuilder,
    ELASTICSEARCH: ElasticSearchConfigInterfaceBuilder,
}
