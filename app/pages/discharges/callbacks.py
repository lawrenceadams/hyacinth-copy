import os
import logging
import asyncio
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dash import Input, Output, callback, no_update

from databases import odbc_cursor, cosmos_client, CosmosDBLongCallbackManager
from ids import STORE_TIMER_5M
from call_model import call_model


AUTO_REFRESH_INTERVAL = 60 * 5
ENVIRONMENT = os.environ.get("ENVIRONMENT", default="dev")
DISCHARGES_QUERY = (Path(__file__).parent / "sql/discharges.sql").read_text()
DEV_QUERY = (Path(__file__).parent / "sql/app-dev.sql").read_text()
cosmos = cosmos_client()


async def fetch_prediction(app_to_call_id, payload):
    return await asyncio.to_thread(call_model, app_to_call_id, payload)

async def fetch_predictions(patients):
    logging.info("Fetching predictions")
    predictions = await asyncio.gather(
        *[fetch_prediction("los-predictor", f'{{"csn": {patient["mrn"]}}}') for patient in patients]
    )
    return predictions

if cosmos:
    cosmosdb_callback_manager = CosmosDBLongCallbackManager(
        cosmos_client(),
        database_name="hyacinth-state",
        container_name="hyacinth",
        expire=AUTO_REFRESH_INTERVAL,
        partition_key="/Id",
    )

def _fetch_discharges():
    logging.info("Fetching discharges from SQL store")

    if ENVIRONMENT != "prod":
        df = pd.read_sql(DEV_QUERY, odbc_cursor().connection)
        df.columns = ["mrn", "firstname", "sex", "department"]
    else:
        data = pd.read_sql(DISCHARGES_QUERY, odbc_cursor().connection)
        beds = pd.read_json("assets/locations/bed_defaults.json")
        df = data.merge(
            beds[["location_string", "department", "room", "location_name"]],
            how="left",
            left_on="hl7_location",
            right_on="location_string",
        )
    logging.info(f"Fetched {len(df)} rows from SQL store")

    patients = df.to_dict("records")
    predictions = asyncio.run(fetch_predictions(patients))

    df["prediction"] = predictions
    df = df.sort_values(by="prediction", ascending=False)
    return df

@callback(
        Output("loading_overlay", "children"),
        Input("update_button", "n_clicks")
)
def _reload(n_clicks):
    return no_update

@callback(
    Output("discharges_table", "data"),
    Output("update_button", "children"),
    Input("update_button", "n_clicks"),
    Input(STORE_TIMER_5M, "n_intervals"),
    # Input("discharges_table", "page_current"),
    # Input("discharges_table", "page_size"),
)
def _get_discharges(n_clicks, n_intervals):
    now = datetime.now(timezone.utc)
    if cosmos:
        cached_data = cosmosdb_callback_manager.get("discharges_cache")
        if cached_data:
            logging.info("Retrieved cached data.")
            df = cached_data
            return (
                cached_data,
                f"Retrieved from Cache at {now:%H:%M:%S}",
            )

    logging.info("Refreshing cached data")
    df = _fetch_discharges()
    last_updated = now

    if cosmos:
        cosmosdb_callback_manager.set(
            cache_key="discharges_cache", value=df.to_dict("records")
    )
        
    return (
        df.to_dict("records"),
        f"Retrieved from Feature Store. Last updated at {last_updated:%H:%M:%S}",
    )

