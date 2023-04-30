import dash
import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify
from databases import cosmos_client


dash.register_page(__name__, path="/", name="Home")

timers = html.Div([])
stores = html.Div([])

_inline = {"display": "inline"}

body = html.Div(
    [
        dmc.Paper(
            children=[
                dmc.Title(
                    children=[
                        "Welcome ",
                        DashIconify(icon="mdi:greeting-outline", inline=True),
                    ],
                    color="#5c7cfa",
                ),
                dmc.Divider(),
                dmc.Text("""This is a demo FlowEHR application. """),
            ],
            style={"padding": "1rem"},
        ),
    ],
    style={"padding": "1rem"},
)


# from azure.cosmos import PartitionKey

# cosmos = cosmos_client()

# #db = cosmos.get_database_client("rhubarb_ui-state")
# db = cosmos.create_database("hyacinth-state")
# new_container_id = "discharges"
# new_container_pk = PartitionKey(path="/id")
# new_container = db.create_container_if_not_exists(
#     id=new_container_id, partition_key=new_container_pk,
#     offer_throughput=400
# )

# container_client = cosmos_database.get_container("hyacinth")

# item = {"id": "1", "rhubarb": "TRUE", "why": "hyacinth"}

# container_client.upsert_item(item)

def layout() -> dash.html.Div:
    return html.Div(
        children=[
            timers,
            stores,
            body,
        ]
    )
