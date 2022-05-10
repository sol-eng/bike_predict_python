#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
from pins import board_rsconnect
from dotenv import load_dotenv
import os
import xgboost as xgb
from datetime import datetime, timedelta
from vetiver import VetiverModel, VetiverAPI, vetiver_endpoint
import joblib
load_dotenv()


board = board_rsconnect(
    server_url="https://colorado.rstudio.com/rsc/",
    api_key=os.getenv("CONNECT_API_KEY")
)
#> Connecting to RSC 1.9.0.1 at <https://connect.rstudioservices.com>


# In[3]:


reg = board.pin_read(name="xu.fei/bike_xgboost_6m")


# df.date = pd.to_datetime(df.date)


# # In[7]:


# df.columns = ['id', 'hour', 'date', 'month', 'dow', 'n_bikes', 'lat', 'lon']


# # In[10]:


# N_DAYS_AGO = 15


# # In[11]:


# date_N_days_ago = df.date.max() - timedelta(days=N_DAYS_AGO)


# # In[13]:


# df_train = df.loc[df.date < date_N_days_ago]


# df_test = df.loc[df.date >= date_N_days_ago]


# df_train_6m = df_train.iloc[:int(6e6), :]


# def get_features(df: pd.DataFrame, label: str=None) -> pd.DataFrame:
#     """
#     Get time series features from dataframe
#     """
#     ds = df['date'].dt
#     df['dayofweek'] = ds.dayofweek
#     df['quarter'] = ds.quarter
#     df['month'] = ds.month
#     df['year'] = ds.year
#     df['dayofyear'] = ds.dayofyear
#     df['dayofmonth'] = ds.day
#     df['weekofyear'] = ds.isocalendar().week.astype(int)
#     X = df[[
#         'hour','dayofweek','quarter','month','year',
#         'dayofyear','dayofmonth','weekofyear','lat','lon'
#     ]]
#     if label:
#         y = df[label]
#         return X, y
#     return X

# X_train, y_train = get_features(df_train_6m, label='n_bikes')


# X_test, y_test = get_features(df_test, label='n_bikes')


# reg = xgb.XGBRegressor(n_estimators=1000)
# reg.fit(
#     X_train, y_train,
#     eval_set=[(X_train, y_train), (X_test, y_test)],
#     early_stopping_rounds=10,
#     verbose=True) 

# reg = joblib.load('.notebooks/bike_xgboost.joblib')

v = VetiverModel(reg, save_ptype = True, model_name="bikeshare_xgboost")

app = VetiverAPI(v, check_ptype=True)

api = app.app
app.run()