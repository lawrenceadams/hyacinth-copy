# 🟪 Hyacinth  
[![Deploy prod](https://github.com/UCLH-FlowEHR-Bed/hyacinth/actions/workflows/deploy_prod.yml/badge.svg?branch=prod)](https://github.com/UCLH-FlowEHR-Bed/hyacinth/actions/workflows/deploy_prod.yml)
[![Deploy app-dev](https://github.com/UCLH-FlowEHR-Bed/hyacinth/actions/workflows/deploy_app-dev.yml/badge.svg)](https://github.com/UCLH-FlowEHR-Bed/hyacinth/actions/workflows/deploy_app-dev.yml)

A simple application built with [Plotly Dash](https://dash.plotly.com) and [Dash Mantine Components](https://dash-mantine-components.com), for demonstration of FlowEHR, an open-source, safe, secure platform for research and development in digital healthcare. 

The application displays length-of-stay predictions based on the [los_predictor](https://github.com/UCLH-FlowEHR-Bed/los_predictor). It pulls features from an Azure-hosted MSSQL feature store, and stores its state in a CosmosDB database. 

Further information on the model can be found on the [LOS Predictor model card](https://github.com/UCLH-FlowEHR-Bed/hyacinth/blob/prod/app/assets/los_model.md). This repository is based on the open source [Dash Seedling](https://github.com/UCLH-Foundry/Dash-Seedling)
