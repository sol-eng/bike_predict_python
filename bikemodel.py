#!/usr/bin/env python
# coding: utf-8

from pins import board_rsconnect
from dotenv import load_dotenv
import os
from vetiver import VetiverModel, VetiverAPI
load_dotenv()


board = board_rsconnect(
    server_url="https://colorado.rstudio.com/rsc/",
    api_key=os.getenv("API_KEY"), allow_pickle_read=True
)

rf = board.pin_read(name="gagan/bikeshare-rf")
X_train = board.pin_read(name="gagan/bike_x_train")

v = VetiverModel(rf, save_ptype = True, ptype_data=X_train, model_name="bikeshare_xgboost")

app = VetiverAPI(v, check_ptype=True)

api = app.app
