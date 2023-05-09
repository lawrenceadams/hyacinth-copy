import os
import logging
# import asyncio
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from dash import Input, Output, callback, no_update
import plotly.express as px
import pickle
import codecs

from databases import sqlalchemy_connection, cosmos_client, CosmosDBLongCallbackManager
from sqlalchemy import text
from ids import STORE_TIMER_5M
from call_model import call_model


AUTO_REFRESH_INTERVAL = 60 * 5
ENVIRONMENT = os.environ.get("ENVIRONMENT", default="dev")
DISCHARGES_QUERY = text((Path(__file__).parent / "sql/discharges.sql").read_text())
DEV_QUERY = text((Path(__file__).parent / "sql/app-dev.sql").read_text())
DATABASE_KEY = "database_cache"

cosmos = cosmos_client()
use_cosmos = False

try: 
    cosmosdb_callback_manager = CosmosDBLongCallbackManager(
        cosmos_client(),
        database_name="hyacinth-state",
        container_name="hyacinth",
        expire=(60*2),
        partition_key="/id",
    )
    use_cosmos = True
except:
    pass

# async def _async_fetch_prediction(app_to_call_id, payload):
#     return await asyncio.to_thread(call_model, app_to_call_id, payload)

# async def _async_fetch_predictions(patients):
#     logging.info("Fetching predictions")
#     predictions = await asyncio.gather(
#         *[_async_fetch_prediction("los-predictor", f'{{"csn": {patient["mrn"]}}}') for patient in patients]
#     )
#     return predictions

def _fetch_prediction(app_to_call_id, payload):
    try:
        pred = call_model(app_to_call_id, payload)
        logging.warn(pred)
        if "outputs" in pred and len(pred["outputs"]) > 0:
            return pred["outputs"][0]
        else:
            return -1
    except:
        return -2

def _fetch_predictions(patients):
    logging.info("Fetching predictions")
    predictions = [_fetch_prediction("los-predictor", f'{{"csn": {patient["csn"]}}}') for patient in patients]
    return predictions

def _fetch_discharges():
    logging.info("Fetching discharges from SQL store")
    connection = sqlalchemy_connection()

    if ENVIRONMENT != "prod":
        df = pd.read_sql(DEV_QUERY, connection)
        df.columns = ["mrn", "firstname", "sex", "department"]
    else:
        data = pd.read_sql(DISCHARGES_QUERY, connection)
        beds = pd.read_json("assets/locations/bed_defaults.json")
        df = data.merge(
            beds[["location_string", "department", "room", "location_name"]],
            how="left",
            left_on="hl7_location",
            right_on="location_string",
        )
    logging.info(f"Fetched {len(df)} rows from SQL store")

    patients = df.to_dict("records")
    predictions = _fetch_predictions(patients)

    df["prediction"] = predictions
   # df = df.sort_values(by="prediction", ascending=False)

    connection.close()
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
    Output("inpatient_los_histogram", "figure"),
    Input("update_button", "n_clicks"),
    Input(STORE_TIMER_5M, "n_intervals"),
    # Input("discharges_table", "page_current"),
    # Input("discharges_table", "page_size"),
)
def _get_discharges(n_clicks, n_intervals):
    now = datetime.now(timezone.utc)

    if use_cosmos:
        cached_data = cosmosdb_callback_manager.get(DATABASE_KEY)
        if cached_data:
            logging.info("Retrieved cached data.")
            # Need to decode and unpickle data to ensure datatype consistency
            df = pickle.loads(codecs.decode(cached_data.encode(), "base64"))
            return (
                df.to_dict('records'), 
                f"Retrieved from Cache at {now:%H:%M:%S}",
                px.histogram(df['length_of_stay'])
            )

    logging.info("Refreshing cached data")
    df = _fetch_discharges()

    # Anonymise for demo
    df['firstname'] = '***'
    df['lastname'] = '***'

    # Convert seconds to days
    df['length_of_stay'] = df['length_of_stay'] / (60*60*24)

    # Round current LoS and Average NEWS
    df['avg_news'] = df['avg_news'].round(2)
    df['length_of_stay'] = df['length_of_stay'].round(2)

    if use_cosmos:
        cosmosdb_callback_manager.set(
            # Dump object as base64 encoded pickle file for data consistency
            cache_key=DATABASE_KEY, value=codecs.encode(pickle.dumps(df), "base64").decode()
    )
    
    return (
        df.to_dict('records'),
        f"Retrieved from Feature Store. Last updated at {now:%H:%M:%S}",
        px.histogram(df['length_of_stay'])
    )
