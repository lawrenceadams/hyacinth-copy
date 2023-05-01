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
import logging


auto_refresh_interval = 60 * 5


def _fetch_discharges():
    if os.environ["ENVIRONMENT"] == "prod":
        query = (Path(__file__).parent / "sql/discharges.sql").read_text()
        data = pd.read_sql(query, odbc_cursor().connection)
        beds = pd.read_json("assets/locations/bed_defaults.json")
        df = data.merge(
            beds[["location_string", "department", "room", "location_name"]],
            how="left",
            left_on="hl7_location",
            right_on="location_string",
        )  # .query("department == @dept_selector"))
    else:
        query = (Path(__file__).parent / "sql/app-dev.sql").read_text()
        df = pd.read_sql(query, odbc_cursor().connection)
        df.columns = ["mrn", "firstname", "sex", "department"]
    return df


@callback(
    Output("discharges_table", "data"),
    Output("last_updated_time", "children"),
    Output("refresh_button", "loading"),
    Input("refresh_button", "n_clicks"),
    Input(STORE_TIMER_5M, "n_intervals"),
)
def _get_discharges(n_clicks, n_intervals):
    nc = 0
    now = datetime.now()
    if nc != n_clicks:  # triggering a "refresh"
        logging.info("")
        df = _fetch_discharges()
        nc = n_clicks
        return df, f"Updated manually at {now:%H:%M:%S}", True

    else:  # nc == n_clicks; i.e. interval only
        cosmosdb_callback_manager = CosmosDBLongCallbackManager(
            cosmos_client(),
            database_name="hyacinth-state",
            container_name="hyacinth",
            expire=auto_refresh_interval,
            partition_key="/Id",
        )

        cached_data = cosmosdb_callback_manager.get("discharges_cache")
        last_updated = cosmosdb_callback_manager.get("last_updated")

        if last_updated:  # is not null
            last_updated = datetime.fromisoformat(last_updated)

        if (
            cached_data  # is not null
            and last_updated  # is not null
            and (now - last_updated)
            < timedelta(seconds=auto_refresh_interval)  # within time window
        ):
            return cached_data, f"Last updated at {last_updated:%H:%M:%S}", False

        else:  # if after time window
            df = _fetch_discharges()

            cosmosdb_callback_manager.set(
                cache_key="discharges_cache", value=df.to_dict("records")
            )
            cosmosdb_callback_manager.set(
                cache_key="last_updated", value=now.isoformat()
            )

        return df.to_dict("records"), f"Last updated at {last_updated:%H:%M:%S}", False


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
