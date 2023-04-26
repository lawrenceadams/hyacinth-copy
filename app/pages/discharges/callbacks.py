import pandas as pd
from databases import odbc_cursor
from dash import Input, Output, callback
from pathlib import Path
from pages.discharges import CAMPUSES

@callback(
        Output("discharges_table", "data"),
        Input("dept_selector", "value"),
)
def get_discharges(dept_selector):
    query =(Path(__file__).parent / "sql/discharges.sql").read_text()
    data = pd.read_sql(query, odbc_cursor().connection)
    beds = pd.read_json("assets/locations/bed_defaults.json")
    
    df = (data.merge(beds[['location_string',
                           'department','room',
                           'location_name']],
                      how="left",
                      left_on="hl7_location", 
                      right_on="location_string")
        .query("department == @dept_selector"))

    return df.to_dict('records')



@callback(
    Output("dept_selector", "data"),
    Output("dept_selector", "value"),
    Input("campus_selector", "value"),
)
def get_wards(campus_selector):
    campus_dict = {i.get("value"): i.get("label") for i in CAMPUSES}
    depts = (pd.read_json("assets/locations/departments.json")
             .query('closed_perm_01 != True')
             .query('department.str.startswith(@campus_dict[@campus_selector])')
             .department
             .unique()
             .tolist())
    return depts, depts[0]





