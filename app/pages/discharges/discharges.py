import dash
import dash_mantine_components as dmc
import json
from dash import dash_table as dtable, html
from pathlib import Path
import ids
from dash_iconify import DashIconify

from pages.discharges.callbacks import *

from pages.discharges import CAMPUSES


dash.register_page(__name__, path="/discharges", name="Discharges")

# campus_selector = html.Div(
#     [
#         dmc.SegmentedControl(
#             id="campus_selector",
#             value=[i.get("value") for i in CAMPUSES if i.get("label") == "UCH"][0],
#             data=CAMPUSES,
#             persistence=True,
#             persistence_type="local"
#         ),
#     ]
# )
# dept_selector = dmc.Container(
#     [
#         dmc.Select(
#             placeholder="Select a ward",
#             id="dept_selector",
#             searchable=True,
#             persistence=False,
#         ),
#     ],
#     fluid=True,
#     p="xxs",
# )

refresh_button = dmc.Button(
    dmc.Text(id="last_updated_time", children="Not yet updated"),
    id="refresh_button",
    leftIcon=DashIconify(icon="fluent:database-plug-connected-20-filled"),
    color="blue",
)

discharges_table = dmc.Paper(
    dtable.DataTable(
        id="discharges_table",
        columns=[
            {"id": "department", "name": "Ward"},
            {"id": "room", "name": "Bed"},
            {"id": "mrn", "name": "MRN"},
            {"id": "firstname", "name": "First Name"},
            {"id": "lastname", "name": "Last Name"},
            {"id": "sex", "name": "Sex"},
            {"id": "avg_news", "name": "NEWS"},
            {"id": "admission_datetime", "name": "Admission Date"},
            {"id": "length_of_stay", "name": "Length of Stay"},
        ],
        style_table={"overflowX": "scroll"},
        style_as_list_view=True,  # remove col lines
        style_cell={
            "fontSize": 11,
            "padding": "5px",
        },
        style_data={"color": "black", "backgroundColor": "white"},
        # striped rows
        markdown_options={"html": True},
        persistence=False,
        persisted_props=["data"],
        sort_action="native",
        filter_action="native",
        filter_query="",
    ),
    shadow="lg",
    p="md",  # padding
    withBorder=True,
)


debug_inspector = dmc.Container(
    [
        dmc.Spoiler(
            children=[
                dmc.Prism(
                    language="json",
                    # id=ids.DEBUG_NODE_INSPECTOR_WARD, children=""
                )
            ],
            showLabel="Show more",
            hideLabel="Hide",
            maxHeight=100,
        )
    ]
)


body = dmc.Container(
    [
        dmc.Grid(
            children=[
                # dmc.Col(campus_selector, span=3),
                # dmc.Col(dept_selector, span=6),
                dmc.Col(refresh_button, span=3),
                dmc.Col(discharges_table, span=12),
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
            # debug_inspector,
        ]
    )
