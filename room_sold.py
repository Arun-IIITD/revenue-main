import base64
import os
from io import BytesIO
#from streamlit_extras.switch_page_button import switch_page
from statistics import mean
import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pymongo
import streamlit as st
from prophet import Prophet
from prophet.plot import add_changepoints_to_plot
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from CAL import perform

connection_uri = "mongodb+srv://annu21312:6dPsrXPfhm19YxXl@hello.hes3iy5.mongodb.net/"
client = pymongo.MongoClient(connection_uri, serverSelectionTimeoutMS=30000)
database_name = "Revenue_Forecasting"
db = client[database_name] 

collection4 = db["Accuracy"]
cursor4 = collection4.find({})
data4 = pd.DataFrame(list(cursor4))
data4 = data4.drop_duplicates() 

collection5 = db["Revenue"]
cursor5 = collection5.find({})
data5 = pd.DataFrame(list(cursor5))
data5 = data5.drop_duplicates() 

data4 =  data4[['Business Date','Room Revenue','Rooms Sold']]
data5 = data5[['Business Date','Room Revenue','Rooms Sold','Arrival Rooms','Individual Revenue','Individual Confirm']]
data6 = pd.concat([data4,data5],ignore_index=True)

data6 = data6[['Business Date','Rooms Sold']]
data6.columns = ['ds','y'] 
data6['ds'] = pd.to_datetime(data6['ds'])
data6 = data6.drop_duplicates()  
data6 = data6.sort_values(by='ds')
train_data = data6.iloc[120:775]
test_data = data6.iloc[775:865]
#print(data6.iloc[520])

def prophet():
# Fit the model with the training data
    model = Prophet(
        changepoint_prior_scale=0.09,
        holidays_prior_scale=0.8,
        n_changepoints=500,
        seasonality_mode='multiplicative',
        weekly_seasonality=True,
        daily_seasonality=True,
        yearly_seasonality=True,
        interval_width=0.95
    )
    model.fit(train_data)
    future_for_365_days = model.make_future_dataframe(periods=90, freq='D', include_history=False)
    forecast = model.predict(future_for_365_days)
    forecast = forecast.set_index('ds')[['yhat']].join(test_data.set_index('ds'))

    forecast['Daily Accuracy'] = 1 - (np.abs(forecast['y'] - forecast['yhat']) / forecast['y']).clip(lower=0)
    forecast['Weekly Accuracy'] = forecast['Daily Accuracy'].resample('W').mean()
    forecast['Monthly Accuracy'] = forecast['Daily Accuracy'].resample('M').mean()
    forecast['Yearly Accuracy'] = forecast['Daily Accuracy'].resample('A').mean()

    forecast.reset_index(inplace=True)

    results_df = forecast[['ds', 'y', 'yhat', 'Daily Accuracy', 'Weekly Accuracy', 'Monthly Accuracy', 'Yearly Accuracy']]
    results_df['Weekly Accuracy'].ffill(inplace=True)
    results_df['Monthly Accuracy'].ffill(inplace=True)
    results_df['Yearly Accuracy'].ffill(inplace=True)

    

    # Convert to datetime and extract year and month
    data6['ds'] = pd.to_datetime(data6['ds'])
    data6['Year'] = data6['ds'].dt.year
    data6['Month'] = data6['ds'].dt.strftime('%B')  # Month in full name
    month_order = [ 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    data6['Month'] = pd.Categorical(data6['Month'], categories=month_order, ordered=True)
    data_2022 = data6[data6['Year'] == 2022]
    data_2023 = data6[data6['Year'] == 2023]
    monthly_total_revenue_2022 = data_2022.groupby('Month')['y'].sum().reset_index()
    monthly_total_revenue_2023 = data_2023.groupby('Month')['y'].sum().reset_index()
    merged_data = pd.merge(monthly_total_revenue_2022, monthly_total_revenue_2023, on='Month', suffixes=('_2022', '_2023'))

    return results_df, merged_data
