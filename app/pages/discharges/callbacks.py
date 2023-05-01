import pandas as pd
from databases import odbc_cursor, cosmos_client, CosmosDBLongCallbackManager
from dash import Input, Output, callback
from pathlib import Path
from pages.discharges import CAMPUSES
from datetime import datetime, timedelta
import os
from cachetools import TTLCache
from uuid import uuid4
import diskcache
from azure.cosmos import PartitionKey
from ids import STORE_TIMER_5M

launch_uid = uuid4
auto_refresh_interval = 60 * 5

cache_database = "hyacinth-state"
cache_container = "hyacinth"
partition_key = "/Id"

client = cosmos_client()
cosmos_db = client.get_database_client(cache_database)

pk = PartitionKey(path="/Id")

cosmosdb_callback_manager = CosmosDBLongCallbackManager(
    client,
    cache_database,
    cache_container,
    auto_refresh_interval,
    partition_key,
)


@callback(
    Output("last_updated_time", "children"),
    Input(STORE_TIMER_5M, "n_intervals"),
)
def update_last_updated(n_intervals):
    last_updated = cosmosdb_callback_manager.get("last_updated")

    if last_updated:
        last_updated = datetime.fromisoformat(last_updated)
        last_updated_str = f"Last updated at {last_updated:%H:%M:%S}"
    else:
        last_updated_str = "Last updated time not available"

    return last_updated_str


@callback(
    Output("discharges_table", "data"),
    Output("last_updated_time", "children"),
    Output("refresh_button", "loading"),
    Input("refresh_button", "n_clicks"),
)
def _get_discharges(n_clicks):
    print("getting discharges")
    now = datetime.now()
    cache_key = "discharges_cache"
    cached_data = cosmosdb_callback_manager.get(cache_key)
    last_updated = cosmosdb_callback_manager.get("last_updated")

    if last_updated:
        last_updated = datetime.fromisoformat(last_updated)

    if (
        cached_data
        and last_updated
        and (now - last_updated) < timedelta(seconds=auto_refresh_interval)
    ):
        last_updated_str = (
            f"Last updated at {last_updated:%H:%M:%S}"
            if last_updated
            else "Last updated time not available"
        )
        return cached_data, last_updated_str, False
    if os.environ["ENVIRONMENT"] == "prod":
        query = (Path(__file__).parent / "sql/discharges.sql").read_text()
        data = pd.read_sql(query, odbc_cursor().connection)
        beds = pd.read_json("assets/locations/bed_defaults.json")

        df = data.merge(
            beds[["location_string", "department", "room", "location_name"]],
            how="left",
            left_on="hl7_location",
            right_on="location_string",
        )
    else:
        query = (Path(__file__).parent / "sql/app-dev.sql").read_text()
        df = pd.read_sql(query, odbc_cursor().connection)
        df.columns = ["mrn", "firstname", "sex", "department"]

    # .query("department == @dept_selector"))

    cosmosdb_callback_manager.set(cache_key=cache_key, value=df.to_dict("records"))
    cosmosdb_callback_manager.set(cache_key="last_updated", value=now.isoformat())
    last_updated_str = (
        f"Last updated at {last_updated:%H:%M:%S}"
        if last_updated
        else "Last updated time not available"
    )

    return df.to_dict("records"), last_updated_str, False


# @callback(
#     Output("dept_selector", "data"),
#     Output("dept_selector", "value"),
#     Input("campus_selector", "value"),
# )
# def _get_wards(campus_selector):
#     campus_dict = {i.get("value"): i.get("label") for i in CAMPUSES}
#     depts = (pd.read_json("assets/locations/departments.json")
#              .query('closed_perm_01 != True')
#              .query('department.str.startswith(@campus_dict[@campus_selector])')
#              .department
#              .unique()
#              .tolist())
#     return depts, depts[0]
