import pandas as pd
from databases import odbc_cursor, cosmos_client
from dash import Input, Output, callback, DiskcacheManager
from pathlib import Path
from pages.discharges import CAMPUSES
from datetime import datetime, timedelta
import os 
from uuid import uuid4

launch_uid = uuid4 
auto_refresh_interval = 60*5 
cache_database = "ToDoList"
cache_container = "Items"
container = (cosmos_client()
             .get_database_client(cache_database)
             .get_container_client(cache_container))


background_callback_manager = DiskcacheManager(
    container,
    cache_by=[lambda: uuid4().hex],
    expire=auto_refresh_interval  # Cache expiration time in seconds
)

@callback(
        Output("discharges_table", "data"),
        Output("last_updated_time", "children"),
        Output("refresh_button", "loading"),
        Input ("refresh_button", "n_clicks"),
)
def _get_discharges():
    print("getting discharges")
    now=datetime.now()
    cache_key= "discharges_cache"
    cached_data = background_callback_manager.get(cache_key)
    last_updated = background_callback_manager.get("last_updated")


    if cached_data and last_updated and (now - last_updated) < timedelta(seconds=auto_refresh_interval):
        return cached_data, f"Last updated at {last_updated:%H:%M:%S}", False
            
    query =(Path(__file__).parent / "sql/discharges.sql").read_text()
    data = pd.read_sql(query, odbc_cursor().connection)
    beds = pd.read_json("assets/locations/bed_defaults.json")
    
    df = (data.merge(beds[['location_string',
                           'department','room',
                           'location_name']],
                      how="left",
                      left_on="hl7_location", 
                      right_on="location_string"))
 
        # .query("department == @dept_selector"))
 
    background_callback_manager.set(cache_key, df.to_dict('records'))
    background_callback_manager.set("last_updated", now)

    return df.to_dict('records'), f"Last updated at {last_updated:%H:%M:%S}", False

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
