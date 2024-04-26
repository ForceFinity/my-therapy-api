import os

import asyncpg
from google.cloud.sql.connector import Connector, IPTypes

connector = Connector()


def conn_cloud_sql() -> asyncpg.Connection:
    instance_connection_name = os.environ[
        "INSTANCE_CONNECTION_NAME"
    ]

    return connector.connect(
        instance_connection_name,
        "asyncpg",
        user="postgres",
        password="sigmabear",
        db="postgres",
        ip_type=IPTypes.PUBLIC
        # db_user=os.environ["DB_USER"],  # e.g. 'my-db-user'
        #     db_pass=os.environ["DB_PASS"],  # e.g. 'my-db-password'
        #     db_name=os.environ["DB_NAME"]  # e.g. 'my-database'
    )
