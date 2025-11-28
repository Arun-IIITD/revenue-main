# 00 - 07 Days: 98% 
# 08 - 14 Days: 94%
# 15 - 21 Days: 90%
# 22 - 30 Days: 86%
# 31 - 60 Days: 75%
# 60 - 90 Days: 65%
# 90 - 365 Days: 50%

import base64
import os
from io import BytesIO
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

data6 = data6[['Business Date','Room Revenue']]
data6.columns = ['ds','y'] 
data6['ds'] = pd.to_datetime(data6['ds'])
data6 = data6.drop_duplicates()  
data6 = data6.sort_values(by='ds')
train_data = data6.iloc[120:775]
test_data = data6.iloc[775:865]

# Fit the model with the training data
# def prophet():
#     model = Prophet(
#         changepoint_prior_scale=0.01,
#         holidays_prior_scale=0.8,
#         n_changepoints=500,
#         seasonality_mode='multiplicative',
#         weekly_seasonality=True,
#         daily_seasonality=True,
#         yearly_seasonality=True,
#         interval_width=0.95
#     )
#     model.fit(train_data)

#     # Generate a future dataframe for the next 90 days
#     future_for_90_days = model.make_future_dataframe(periods=90, freq='D', include_history=False)
#     forecast = model.predict(future_for_90_days)


#     # Initialize an empty list to store accuracy for each day
#     daily_accuracies = []

#     # Loop through each day in the forecast
#     for i in range(90):
#         predicted_value = forecast.iloc[i]['yhat']
#         actual_value = test_data.iloc[i]['y']  # Ensure test_data is correctly aligned with forecast dates

#         # Calculate the accuracy for the day as 1 - absolute percentage error
#         accuracy = 1 - np.abs((actual_value - predicted_value) / actual_value)
#         accuracy = max(0, accuracy)  
#         daily_accuracies.append(accuracy)

  
#     results_df = pd.DataFrame({
#         'Date': forecast['ds'].iloc[:90],
#         'Actual': test_data['y'].values[:90],  
#         'Predicted': forecast['yhat'].iloc[:90],
#         'Accuracy': daily_accuracies
#     })

#     p = results_df['Accuracy'].tolist()
#     accu = []
#     for i in p:
#         i = i*100
#         accu.append(round(i))




def prophet():
    # Initialize the Prophet model with specified parameters
    model = Prophet(
        changepoint_prior_scale=0.01,
        holidays_prior_scale=0.8,
        n_changepoints=500,
        seasonality_mode='multiplicative',
        weekly_seasonality=True,
        daily_seasonality=True,
        yearly_seasonality=True,
        interval_width=0.95
    )
    
    # Fit the model with the training data
    model.fit(train_data)
    
    # Generate a future dataframe for the next 365 days (to ensure coverage of yearly accuracy)
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



    # MERGED DATA
    data6['ds'] = pd.to_datetime(data6['ds'])
    data6['Year'] = data6['ds'].dt.year
    data6['Month'] = data6['ds'].dt.strftime('%B')  
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    data6['Month'] = pd.Categorical(data6['Month'], categories=month_order, ordered=True)
    data_2022 = data6[data6['Year'] == 2022]
    data_2023 = data6[data6['Year'] == 2023]
    monthly_total_revenue_2022 = data_2022.groupby('Month')['y'].sum().reset_index()
    monthly_total_revenue_2023 = data_2023.groupby('Month')['y'].sum().reset_index()
    merged_data = pd.merge(monthly_total_revenue_2022, monthly_total_revenue_2023, on='Month', suffixes=('_2022', '_2023'))

    return results_df, merged_data
A = prophet()
#print(A[0]['Weekly Accuracy'])