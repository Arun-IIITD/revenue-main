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
data1 =  data4[['Business Date','Room Revenue','Rooms Sold']]
data2 = data5[['Business Date','Room Revenue','Rooms Sold','Arrival Rooms','Individual Revenue','Individual Confirm']]
data = pd.concat([data1,data2],ignore_index=True)
data4 = data[['Business Date','Individual Revenue']]
data4.columns = ['ds','y'] 
data4['ds'] = pd.to_datetime(data4['ds'])
data4 = data4.drop_duplicates()  
data4 = data4.sort_values(by='ds')
data4 = data4.drop_duplicates()  
train_data = data4.iloc[520:775]
test_data = data4.iloc[775:865]


def prophet():
    model = Prophet(
        changepoint_prior_scale=0.01,
        holidays_prior_scale=0.8,
        #n_changepoints=500,
        seasonality_mode='multiplicative',
        weekly_seasonality=True,
        daily_seasonality=True,
        yearly_seasonality=True,
        interval_width=0.95
    )
    model.fit(train_data)
      # Generate a future dataframe for the next 365 days (to ensure coverage of yearly accuracy)
    future_for_365_days = model.make_future_dataframe(periods=89, freq='D', include_history=False)
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


    # Convert 'ds' to datetime
    data4['ds'] = pd.to_datetime(data4['ds'])

    # Extract year and month
    data4['Year'] = data4['ds'].dt.year
    data4['Month'] = data4['ds'].dt.strftime('%B')  # Month in full name

    # Filter for the year 2023
    data_2023 = data4[data4['Year'] == 2023]

    # Define the month order
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June', 
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    # Make 'Month' a categorical column with a specified order
    data_2023['Month'] = pd.Categorical(data_2023['Month'], categories=month_order, ordered=True)

    # Group by month and sum the revenues for 2023
    merged_data = data_2023.groupby('Month')['y'].sum().reset_index()

    return results_df, merged_data

