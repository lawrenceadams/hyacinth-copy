import os
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

from dash import Input, Output, callback

from databases import odbc_cursor, cosmos_client, CosmosDBLongCallbackManager
from ids import STORE_TIMER_5M

AUTO_REFRESH_INTERVAL = 60 * 5

# Read SQL queries
DISCHARGES_QUERY = (Path(__file__).parent / "sql/discharges.sql").read_text()
DEV_QUERY = (Path(__file__).parent / "sql/app-dev.sql").read_text()

# Auto-refresh triggered
cosmosdb_callback_manager = CosmosDBLongCallbackManager(
    cosmos_client(),
    database_name="hyacinth-state",
    container_name="hyacinth",
    expire=AUTO_REFRESH_INTERVAL,
    partition_key="/Id",
)


def _fetch_discharges():
    logging.info("Fetching discharges from SQL store")
    if os.environ["ENVIRONMENT"] == "prod":
        data = pd.read_sql(DISCHARGES_QUERY, odbc_cursor().connection)
        beds = pd.read_json("assets/locations/bed_defaults.json")
        df = data.merge(
            beds[["location_string", "department", "room", "location_name"]],
            how="left",
            left_on="hl7_location",
            right_on="location_string",
        )
    else:
        df = pd.read_sql(DEV_QUERY, odbc_cursor().connection)
        df.columns = ["mrn", "firstname", "sex", "department"]
    logging.info(f"Fetched {len(df)} rows from SQL store")
    return df


# @callback(
#     Output("update_button", "loading", allow_duplicate=True),
#     Input("update_button", "n_clicks"),
#     prevent_initial_call="initial_duplicate",
# )
# def _make_button_load(n_clicks):
#     return True


@callback(
    Output("discharges_table", "data"),
    Output("update_button", "children"),
    Input("update_button", "n_clicks"),
    Input(STORE_TIMER_5M, "n_intervals"),
)
def _get_discharges(n_clicks, n_intervals):
    now = datetime.now()
    last_updated = cosmosdb_callback_manager.get("last_updated")
    cached_data = cosmosdb_callback_manager.get("discharges_cache")

    if cached_data:
        logging.info("Retrieved cached data.")
        df = cached_data
        return (
            cached_data,
            f"Retrieved from Cache. ",  # Last updated at {last_updated:%H:%M:%S}",
        )

    logging.info("Refreshing cached data")
    df = _fetch_discharges()
    last_updated = now

    cosmosdb_callback_manager.set(
        cache_key="discharges_cache", value=df.to_dict("records")
    )
    cosmosdb_callback_manager.set(cache_key="last_updated", value=now)
    return (
        df.to_dict("records"),
        f"Retrieved from Feature Store. Last updated at {last_updated:%H:%M:%S}",
    )
