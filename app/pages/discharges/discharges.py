import dash
import dash_mantine_components as dmc
import json
from dash import dash_table as dtable, html, dcc
from pathlib import Path
import ids
from dash_iconify import DashIconify

from pages.discharges.callbacks import *

from pages.discharges import CAMPUSES


dash.register_page(__name__, path="/discharges", name="Discharges")

updated_time = dmc.Button(
    id="update_button", children="Not updated yet", color="blue", fullWidth=True
)

loading_overlay = dmc.LoadingOverlay(id="loading_overlay", children=updated_time)

discharges_table = dmc.Paper(
    dtable.DataTable(
        id="discharges_table",
        columns=[
            {"id": "department", "name": "Ward"},
            {"id": "room", "name": "Bed"},
            # {"id": "csn", "name": "CSN"},
            {"id": "firstname", "name": "First Name"},
            {"id": "lastname", "name": "Last Name"},
            {"id": "sex", "name": "Sex"},
            {"id": "avg_news", "name": "NEWS"},
            {"id": "admission_datetime", "name": "Admission Date"},
            {"id": "length_of_stay", "name": "Length of Stay"},
            {"id": "prediction", "name": "Predictions"},
        ],
        style_table={"overflowX": "scroll"},
        style_as_list_view=True,
        style_cell={
            "fontSize": 11,
            "padding": "5px",
        },
        # style_data={"color": "black", "backgroundColor": "red"},
        # striped rows
        markdown_options={"html": True},
        persistence=False,
        persisted_props=["data"],
        sort_action="native",
        filter_action="native",
        filter_query="",
        # page_current=0,
        # page_size=20,
        # page_action='custom'
        # Highlight if going to be discharged
        style_data_conditional = [{
            'if': {
                'filter_query': '{prediction} = 1',
            },
            'backgroundColor': '#154734',
            'color': 'white'
        }]
    ),
    shadow="lg",
    p="md",  # padding
    withBorder=True,
)

body = dmc.Container(
    [
        dmc.Grid(
            children=[
                dmc.Col(loading_overlay, span=6),
                dmc.Col(discharges_table, span=12),
            ],
        ),
        dcc.Graph(id="inpatient_los_histogram"),
    ],
    style={"width": "100vw"},
    fluid=True,
)


def layout() -> dash.html.Div:
    return html.Div(
        children=[
            body,
        ]
    )
