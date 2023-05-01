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


# Fetch discharges data based on environment
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


# Callback function to get discharges data
@callback(
    Output("discharges_table", "data"),
    Output("refresh_button", "children"),
    Output("refresh_button", "loading"),
    Input("refresh_button", "n_clicks"),
    Input(STORE_TIMER_5M, "n_intervals"),
)
def _get_discharges(n_clicks, n_intervals):
    nc = 0
    now = datetime.now()

    # Manual refresh triggered
    if n_clicks and n_clicks > nc:
        logging.info("Manual refresh triggered...")

        df = _fetch_discharges()
        nc = n_clicks

        logging.info("Refreshing cached data...")
        cosmosdb_callback_manager.set(
            cache_key="discharges_cache", value=df.to_dict("records")
        )

        cosmosdb_callback_manager.set(cache_key="last_updated", value=now)
        return df.to_dict("records"), f"Updated manually at {now:%H:%M:%S}", True

    logging.info("Retrieving cached data...")
    cached_data = cosmosdb_callback_manager.get("discharges_cache")
    last_updated = cosmosdb_callback_manager.get("last_updated")

    if last_updated:
        logging.info("Retrieved cached data.")
        last_updated = datetime.fromisoformat(last_updated)

    time_since_last_update = now - last_updated if last_updated else None

    # If data is already cached and within the refresh interval
    if (
        cached_data
        and last_updated
        and time_since_last_update < timedelta(seconds=AUTO_REFRESH_INTERVAL)
        # ^^ should not be needed as expiry on cache
    ):
        return cached_data, f"Last updated at {last_updated:%H:%M:%S}", False

    # Refresh data and update cache
    df = _fetch_discharges()
    logging.info("Refreshing cached data")
    cosmosdb_callback_manager.set(
        cache_key="discharges_cache", value=df.to_dict("records")
    )
    cosmosdb_callback_manager.set(cache_key="last_updated", value=now)

    return df.to_dict("records"), f"Last updated at {last_updated:%H:%M:%S}", False
