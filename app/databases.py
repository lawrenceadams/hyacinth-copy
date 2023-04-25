import os
from typing import Any
from dev import db_aad_token_struct


environment = os.environ.get("ENVIRONMENT", default="dev")


def odbc_cursor() -> Any:
    """
    ODBC cursor for running queries against the MSSQL feature store.

    Documentation: https://github.com/mkleehammer/pyodbc/wiki
    """
    import pyodbc

    connection_string = os.environ["FEATURE_STORE_CONNECTION_STRING"]

    if "authentication" not in connection_string.lower():
        SQL_COPT_SS_ACCESS_TOKEN = 1256
        attrs_before = {SQL_COPT_SS_ACCESS_TOKEN: db_aad_token_struct()}
    else:
        attrs_before = {}

    connection = pyodbc.connect(connection_string, attrs_before=attrs_before)
    cursor = connection.cursor()
    logging.info("ODBC connection cursor created.")
    return cursor


def cosmos_client() -> "CosmosClient":
    """
    CosmosDB client for connecting with the state store.

    Documentation: https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/sdk-python
    """
    from azure.cosmos import CosmosClient
    from azure.identity import DefaultAzureCredential

    client = CosmosClient(
        os.environ["COSMOSDB_ENDPOINT"],
        credential=(
            DefaultAzureCredential()
            if environment != "local"
            else os.environ["COSMOSDB_KEY"]
        ),
        connection_verify=(environment != "local"),
    )
    logging.info("Cosmos client created.")
    return client
