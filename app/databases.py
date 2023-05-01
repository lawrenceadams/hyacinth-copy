import os
import logging
import pyodbc
from typing import Any
from dev import db_aad_token_struct
from datetime import datetime
from azure.cosmos import CosmosClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential


environment = os.environ.get("ENVIRONMENT", default="dev")


def odbc_cursor() -> Any:
    """
    ODBC cursor for running queries against the MSSQL feature store.

    Documentation: https://github.com/mkleehammer/pyodbc/wiki
    """

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


class CosmosDBLongCallbackManager:
    def __init__(
        self,
        cosmos_client: CosmosClient,
        database_name: str,
        container_name: str,
        expire: int,
        partition_key: str = None,
    ):
        self.client = cosmos_client
        self.database_name = database_name
        self.container_name = container_name
        self.expire = expire
        self.partition_key = partition_key

    def get_database_client(self):
        return self.client.get_database_client(self.database_name)

    def get_container_client(self):
        return self.get_database_client().get_container_client(self.container_name)

    def get(self, cache_key):
        container = self.get_container_client()
        try:
            item = container.read_item(
                item=cache_key, partition_key=self.partition_key or cache_key
            )
            return item.get("value")
        except ResourceNotFoundError:
            return None

    def set(self, value, cache_key):
        container = self.get_container_client()

        if isinstance(value, datetime):
            value = value.isoformat()
        item = {"id": cache_key, "value": value, "expire": self.expire}

        if self.partition_key is not None:
            item[self.partition_key] = self.partition_key
        try:
            container.upsert_item(item)

        except ResourceExistsError:
            container.replace_item(
                item, item["id"], partition_key=self.partition_key or cache_key
            )

    def delete(self, cache_key):
        container = self.get_container_client()
        container.delete_item(
            item=cache_key, partition_key=self.partition_key or cache_key
        )
