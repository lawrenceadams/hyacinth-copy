#  Copyright (c) University College London Hospitals NHS Foundation Trust
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging
import os
from azure_logging import initialize_logging
from dash import Dash, page_registry
from layout.appshell import create_appshell
# from azure_log_exporter import setup_azurelog_exporter


environment = os.environ.get("ENVIRONMENT", default="dev")

initialize_logging(environment, logging.WARN)
logging.info("Logging initialised.")
instrumentation_key = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING", default="")

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        "assets/style.css",
        # include google fonts
        "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400"
        ";500;900&display=swap",
        "https://use.fontawesome.com/releases/v5.8.1/css/all.css",
    ],
    meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1, maximum-scale=1, "
            "user-scalable=no",
        }
    ],
)

# setup_azurelog_exporter(environment, app.server, instrumentation_key)


app.config.suppress_callback_exceptions = True
app.layout = create_appshell([page_registry.values()])

server = app.server

if __name__ == "__main__":
    logging.info("Starting app...")
    app.run_server(host="0.0.0.0", port=8000, debug=True)
