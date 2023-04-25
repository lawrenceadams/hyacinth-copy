import pandas as pd
from databases import odbc_cursor
from dash import Input, Output, callback
from pathlib import Path

@callback(
        Output("discharges_table", "data"),
        Input("dept_selector", "value"),
        Input("campus_selector", "value"),
)
def get_discharges(dept_selector, campus_selector):
    query =(Path(__file__).parent / "sql/discharges.sql").read_text()
    conn = odbc_cursor().connection
    df = pd.read_sql(query, conn)
    conn.close()
    return df.to_dict('records')