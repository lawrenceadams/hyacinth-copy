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
    id="update_button", children="Not updated yet", 
    color="blue", fullWidth=True
)

update_button_overlay = dmc.LoadingOverlay(id="loading_overlay", 
                                           children=updated_time)

length_of_stay_graph = dcc.Graph(id="inpatient_los_histogram")

with open('assets/los_model.md', 'r') as f:
    model_markdown = f.read()

model_card = dmc.Modal(
    children=dcc.Markdown(model_markdown),
    id="model_card",
    size='80%',
)
modal_button = dmc.Button(
    id="modal_button", children="Model Info", 
    color="blue", fullWidth=True
)

force_refresh_button = dmc.Button(
    id="force_refresh_button", children="Force refresh", 
    color="red", fullWidth=True
)
force_refresh_overlay = dmc.LoadingOverlay(id="force_refresh_overlay", 
                                           children=force_refresh_button)

discharges_table = dmc.Paper(
    dtable.DataTable(
        id="discharges_table",
        columns=[
            {"id": "department", "name": "Ward"},
            {"id": "room", "name": "Bed"},
            # {"id": "csn", "name": "CSN"}, # Used for troubleshooting
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
                dmc.Col(update_button_overlay, span=5),
                dmc.Col(force_refresh_overlay, span=5),
                dmc.Col(modal_button, span=2),
                dmc.Col(discharges_table, span=12),
                dmc.Col(length_of_stay_graph, span=12),
                dmc.Col(model_card)
            ],
        ),
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
