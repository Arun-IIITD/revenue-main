# 00 - 07 Days: 98% +
# 08 - 14 Days: 94% + 
# 15 - 21 Days: 90% +

#89 - 0.01
#80 - 0.01
#88 - 0.17

import base64
import os
from io import BytesIO
from statistics import mean
import altair as alt
import holidays
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pymongo
import streamlit as st
from prophet import Prophet
from prophet.plot import (add_changepoints_to_plot, plot, plot_components,plot_components_plotly, plot_plotly)
from sklearn.metrics import (confusion_matrix, mean_absolute_error,mean_absolute_percentage_error,mean_squared_error, recall_score)
from statsmodels.tsa.arima.model import ARIMA
#from CAL import perform

st.set_page_config(page_title="Revenue Forecasting", page_icon=":overview", layout="wide", initial_sidebar_state="collapsed")

def set_custom_styles():
    """
    Custom styles to hide Streamlit general elements and adjust margins.
    """

    custom_styles="""
    <style>
    MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility:hidden;}
    body {
        margin: 0;
        padding: 0;
        font-family: "Helvetica", sans-serif;
    }
    [data-testid="collapsedControl"] {
        display: none
    }     
    .main {
        # margin-left: -80px;
        padding: 20px;
        # margin-top:  -110px; 
        margin-left: -3rem;
        margin-top: -7rem;
        margin-right: -103rem;
    }
    .section-title {
        font-weight: bold;
        font-size: 24px;
    }
    .big-text {
        font-size: 20px;
    }

    .small-text {
        font-size: 14px;
    }

    </style>
    """
    st.markdown(custom_styles, unsafe_allow_html=True)

def custom_top_bar(selected_page=None):
    """
    Custom HTML for a fixed top bar.
    """
    selected_page = selected_page or "trend"
    current_file = os.path.basename(__file__)
    custom_top_bar = f"""
    <style>
        #top-bar {{
            padding: 10px;
            # border-bottom: 1px solid #555;
            border-bottom: 1px solid #ccc;
            # color: black;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        #top-bar h3 {{
            padding: 10px;
            font-weight: bold;
            font-size: 24px;
        }}
        #nav-links {{
            display: flex;
            align-items: center;
        }}
        #nav-links a {{            
            text-decoration: none;
            margin-right: 20px;
            font-size: 16px;
            # font-family: "Source Sans Pro", sans-serif;
            # font-weight: 400;
            # transition: color 0.3s ease-in-out;
        }}
        #nav-links a:hover {{
            # color: #00bcd4;
            color: rgb(255, 75, 75);
        }}
    </style>
    <div id="top-bar">
        <h3 style="font-weight: bold; color: grey;">Revenue Forecasting</h3>
        <div id="nav-links">
            <a style="color: {'red' if selected_page == 'Home' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'Home' else 'none'}" href="/Home" target="_self">Home</a>
            <a style="color: {'red' if selected_page == 'Daily_Overview' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'Daily_Overview' else 'none'}" href="/Daily_Overview" target="_self">Daily Overview</a>
            <a style="color: {'red' if selected_page == 'Revenue_Analysis' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'Revenue_Analysis' else 'none'}" href="/Revenue_Analysis" target="_self">Revenue Analysis</a>
            <a style="color: {'red' if selected_page == 'Report' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'Report' else 'none'}" href="/Report" target="_self">Report</a>
            <a style="color: {'red' if selected_page == 'Upload' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'Upload' else 'none'}" href="/Upload" target="_self">Manage Collections</a>
            <a style="color: {'red' if selected_page == 'market' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'market' else 'none'}" href="/market" target="_self">market</a>
            <a style="color: {'red' if selected_page == 'Prediction' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'Prediction' else 'none'}" href="/Prediction" target="_self">Prediction</a>
            <a style="color: {'red' if selected_page == 'Trend' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'Trend' else 'none'}" href="/Trend" target="_self">Trend</a>
            </div>
    </div>
    """
    st.markdown(custom_top_bar, unsafe_allow_html=True)

# custom_top_bar()
set_custom_styles()

url_path = st.experimental_get_query_params().get("pages", [""])[0]
url_to_page = {
    "/Home": "Home",
    "/Daily_Overview": "Daily_Overview",
    "/Revenue_Analysis": "Revenue_Analysis",
    "/Report": "Report",
   # "/Prediction": "Prediction",
    "/upload": "Upload",
    "/market": "market",
    "/Prediction": "Prediction",
    "/Trend": "Trend",
    #"/Yearly": "Yearly"
}
selected_page = url_to_page.get(url_path)
custom_top_bar(selected_page)

#-------------------------------------------------------


def calculate_day_to_day_ape(actual, predicted):
    actual, predicted = np.array(actual), np.array(predicted)
    return np.abs((actual - predicted) / actual) * 100
# -----------------------------------------------
def plot_revenue_with_error(actual_dates, actual_revenue, predicted_dates, predicted_revenue,range1):
    # Calculate day-to-day APE
    daily_ape = calculate_day_to_day_ape(actual_revenue, predicted_revenue)

    # Create figure and primary axis
    fig = go.Figure()
    
    # Plot actual revenue
    fig.add_trace(go.Scatter(x=actual_dates, y=actual_revenue, mode='lines+markers',
                             name='Actual Revenue', line=dict(color='blue')))
    #yaxis=dict(title='Revenue (in Lakhs)', range=[100000,2000000])
    # Plot predicted revenue
    fig.add_trace(go.Scatter(x=predicted_dates, y=predicted_revenue, mode='lines+markers',
                             name='Predicted Revenue', line=dict(color='red')))
    
    # Add secondary axis for the error rate
    fig.add_trace(go.Scatter(x=actual_dates, y=daily_ape, mode='lines+markers',
                             name='Error Rate (%)', yaxis='y2', line=dict(color='green')))
    
    # Layout adjustments
    fig.update_layout(
        title="ERROR RATE",
        xaxis_title='Date',
        #yaxis=dict(title='Revenue'),
        yaxis=dict(title='Revenue (in Lakhs)', range=range1),
        yaxis2=dict(title='Error Rate (%)', overlaying='y', side='right', range=[0,100]),  # Secondary y-axis for error rate
        legend=dict(x=0.01, y=0.99, bordercolor='Black', borderwidth=1)
    )
    
    # Plot the figure in Streamlit
    st.plotly_chart(fig)

# ---------------------------------------------------------------------


def main():
    st.markdown(
        """
        <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: center;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .input-section {
            margin-bottom: 20px;
        }
        .button-section {
            text-align: center;
        }
        .download-section {
            margin-top: 20px;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
  
    
    

    #EXTRACTING DATABASE
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
    data = pd.concat([data4,data5],ignore_index=True)
    
    data = data[['Business Date','Room Revenue']]
    data.columns = ['ds','y'] 
    data['ds'] = pd.to_datetime(data['ds'])
    data = data.drop_duplicates()  
    data = data.sort_values(by='ds')
    train_data = data.iloc[122:844]
    test_data_for_21_days = data.iloc[844:865]

    st.subheader('ROOM REVENUE')
    st.subheader('Forecast without Tuning')
    col1,col2 = st.columns(2)
    with col1:
        model = Prophet()
        model.fit(train_data)
        future = model.make_future_dataframe(periods=21)
        forecast = model.predict(future)
        fig1 = model.plot(forecast)
        st.pyplot(fig1)
        train_forecast = model.predict(train_data[['ds']])
        val_forecast = model.predict(test_data_for_21_days[['ds']])
        train_mape = mean_absolute_percentage_error(train_data['y'], train_forecast['yhat'])
        val_mape = mean_absolute_percentage_error(test_data_for_21_days['y'], val_forecast['yhat'])
        plot_revenue_with_error(train_forecast['ds'],train_data['y'],train_forecast['ds'],train_forecast['yhat'],[0,2000000])
        st.write(f"TRAIN_MAPE: {(train_mape)}")
        st.write(f'VALIDATION_MAPE: {val_mape}')

    #PROPHET MODEL WITH CHANGEPOINTS for revenue
    st.subheader('Forecast with changepoints')
    col3,col4 = st.columns(2)
    with col3:
        fig2 = model.plot(forecast)  #2nd graph with changepoints
        a = add_changepoints_to_plot(fig2.gca(), model, forecast)
        st.pyplot(fig2)
        #plot_revenue_with_error(train_forecast['ds'],train_data['y'],train_forecast['ds'],train_forecast['yhat'],[100000,2000000])
        #st.write(f"No. of CHANGEPOITNS found between 2021 and 2024: {(len(model.changepoints))}")
        #st.write(f"**After applying Hyperparameter Tuning,we get changepoint_prior scale:  0.96  ** ")

    #PROPHET MODEL WITH HYPERPARAMETER TUNING FOR REVENUE
    st.subheader('Forecast with TUNING ')
    col5,col6 = st.columns(2)
    with col5:
        # #NO OF CHANGEPOINTS AND CHANGEPOINTS #3RD GRAPH WITH CHANGEPOINTS WITH SOME TUNING by default c =25
        m3_changepoints = (pd.date_range('2022-01-23', '2022-12-01', periods=15).date.tolist() + 
        pd.date_range('2023-01-01', '2023-12-01', periods=10).date.tolist())
        m3 = Prophet(changepoints=m3_changepoints, changepoint_prior_scale=0.87)
        m3 = m3.fit(train_data)
        future3 = m3.make_future_dataframe(periods=21)
        forecast3 = m3.predict(future3)
        fig3  = m3.plot(forecast3) #3rd graph without  changepoint
        st.pyplot(fig3)
        train_forecast = m3.predict(train_data[['ds']])
        val_forecast = m3.predict(test_data_for_21_days[['ds']])
        train_mape = mean_absolute_percentage_error(train_data['y'], train_forecast['yhat'])
        val_mape = mean_absolute_percentage_error(test_data_for_21_days['y'], val_forecast['yhat'].tail(21))
        #st.write(f"**After Hyperparameter Tuning with changepoint_prior scale:  0.96  ** ")
        plot_revenue_with_error(train_forecast['ds'],train_data['y'],train_forecast['ds'],train_forecast['yhat'],[0,2000000])
        st.write(f'Training MAPE: {train_mape}')
        st.write(f'Validation_MAPE: {val_mape}')

    
    
    
    
    
    #PROPHET FORECAST FOR ROOM SOLD
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
    data = pd.concat([data4,data5],ignore_index=True)
    data = data[['Business Date','Rooms Sold']]
    data.columns = ['ds','y'] 
    data['ds'] = pd.to_datetime(data['ds'])
    data = data.drop_duplicates()  
    data = data.sort_values(by='ds')
    train_data = data.iloc[122:844]
    test_data_for_21_days = data.iloc[844:865]
 
    st.subheader('ROOM SOLD')
    st.subheader('Forecast without Tuning ')
    col7,col8 = st.columns(2)
    with col7:
        model = Prophet()
        model.fit(train_data)
        future = model.make_future_dataframe(periods=21)
        forecast = model.predict(future)
        fig1 = model.plot(forecast)
        st.pyplot(fig1)
        train_forecast = model.predict(train_data[['ds']])
        val_forecast = model.predict(test_data_for_21_days[['ds']])
        train_mape = mean_absolute_percentage_error(train_data['y'], train_forecast['yhat'])
        val_mape = mean_absolute_percentage_error(test_data_for_21_days['y'], val_forecast['yhat'])
        plot_revenue_with_error(train_forecast['ds'],train_data['y'],train_forecast['ds'],train_forecast['yhat'],[0,150])
        st.write(f"TRAIN_MAPE: {(train_mape)}")
        st.write(f'VALIDATION_MAPE: {val_mape}')
    
    st.subheader('Forecast with Changepoints ')
    col9,col10 = st.columns(2)
    
    with col9:
        fig2 = model.plot(forecast)  #2nd graph with changepoints
        a = add_changepoints_to_plot(fig2.gca(), model, forecast)
        st.pyplot(fig2)
        #st.write(f"No. of CHANGEPOITNS found between 2021 and 2024: {(len(model.changepoints))}")
        #st.write(f"**After applying Hyperparameter Tuning,we get changepoint_prior scale:  0.01  ** ")
    
    st.subheader('Forecast with TUNING ')
    col11,col12 = st.columns(2)
   
    with col11:
        m3_changepoints = (pd.date_range('2022-01-23', '2022-12-01', periods=15).date.tolist() + 
        pd.date_range('2023-01-01', '2023-12-01', periods=10).date.tolist())
        m3 = Prophet(changepoints=m3_changepoints, changepoint_prior_scale=0.99)
        m3 = m3.fit(train_data)
        future3 = m3.make_future_dataframe(periods=21)
        forecast3 = m3.predict(future3)
        fig3  = m3.plot(forecast3) #3rd graph without  changepoint
        st.pyplot(fig3)
        train_forecast = m3.predict(train_data[['ds']])
        val_forecast = m3.predict(test_data_for_21_days[['ds']])
        train_mape = mean_absolute_percentage_error(train_data['y'], train_forecast['yhat'])
        val_mape = mean_absolute_percentage_error(test_data_for_21_days['y'], val_forecast['yhat'].tail(21))
        plot_revenue_with_error(train_forecast['ds'],train_data['y'],train_forecast['ds'],train_forecast['yhat'],[0,150])
        st.write(f'Training MAPE: {train_mape}')
        st.write(f'Validation_MAPE: {val_mape}')


    # #PROPHET FORECAST FOR ARRIVAL ROOMS
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
    data = pd.concat([data4,data5],ignore_index=True)
    data = data[['Business Date','Arrival Rooms']]
    data.columns = ['ds','y'] 
    data['ds'] = pd.to_datetime(data['ds'])
    data = data.drop_duplicates()  
    data = data.sort_values(by='ds')

    train_data = data.iloc[520:844]
    test_data_for_21_days = data.iloc[844:865]
 
    st.subheader('ARRIVAL ROOMS')
    st.subheader('Forecast without Tuning ')
    col13,col14 = st.columns(2)
    with col13:
        model = Prophet()
        model.fit(train_data)
        future = model.make_future_dataframe(periods=21)
        forecast = model.predict(future)
        fig1 = model.plot(forecast)
        st.pyplot(fig1)
        train_forecast = model.predict(train_data[['ds']])
        val_forecast = model.predict(test_data_for_21_days[['ds']])
        train_mape = mean_absolute_percentage_error(train_data['y'], train_forecast['yhat'])
        val_mape = mean_absolute_percentage_error(test_data_for_21_days['y'], val_forecast['yhat'])
        plot_revenue_with_error(train_forecast['ds'],train_data['y'],train_forecast['ds'],train_forecast['yhat'],[0,90])
        st.write(f"TRAIN_MAPE: {(train_mape)}")
        st.write(f'VALIDATION_MAPE: {val_mape}')

    st.subheader('Forecast with Changepoints ')
    col15,col16 = st.columns(2)
    with col15:
        fig2 = model.plot(forecast)  #2nd graph with changepoints
        a = add_changepoints_to_plot(fig2.gca(), model, forecast)
        st.pyplot(fig2)
    
    st.subheader('Forecast with TUNING ')
    col17,col18 = st.columns(2)
    with col17:
        m3_changepoints = pd.date_range('2023-03-10', '2023-12-01', periods=10).date.tolist()
        m3 = Prophet(changepoints=m3_changepoints, changepoint_prior_scale=0.1)
        m3 = m3.fit(train_data)
        future3 = m3.make_future_dataframe(periods=21)
        forecast3 = m3.predict(future3)
        fig3  = m3.plot(forecast3) #3rd graph without  changepoint
        st.pyplot(fig3)
        train_forecast = m3.predict(train_data[['ds']])
        val_forecast = m3.predict(test_data_for_21_days[['ds']])
        train_mape = mean_absolute_percentage_error(train_data['y'], train_forecast['yhat'])
        val_mape = mean_absolute_percentage_error(test_data_for_21_days['y'], val_forecast['yhat'].tail(21))
        plot_revenue_with_error(train_forecast['ds'],train_data['y'],train_forecast['ds'],train_forecast['yhat'],[0,90])
        st.write(f'Training MAPE: {train_mape}')
        st.write(f'Validation_MAPE: {val_mape}')
    

    # #PROPHET FORECAST FOR INDIVIDUAL CONFIRM
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
    data = pd.concat([data4,data5],ignore_index=True)
    data = data[['Business Date','Individual Confirm']]
    data.columns = ['ds','y'] 
    data['ds'] = pd.to_datetime(data['ds'])
    data = data.drop_duplicates()  
    data = data.sort_values(by='ds')
    train_data = data.iloc[520:844]
    test_data_for_21_days = data.iloc[844:865]
 
    st.subheader('INDIVIDUAL CONFIRM')
    st.subheader('Forecast without Tuning ')
    col19,col20 = st.columns(2)
    with col19:
        model = Prophet()
        model.fit(train_data)
        future = model.make_future_dataframe(periods=21)
        forecast = model.predict(future)
        fig1 = model.plot(forecast)
        st.pyplot(fig1)
        train_forecast = model.predict(train_data[['ds']])
        val_forecast = model.predict(test_data_for_21_days[['ds']])
        train_mape = mean_absolute_percentage_error(train_data['y'], train_forecast['yhat'])
        val_mape = mean_absolute_percentage_error(test_data_for_21_days['y'], val_forecast['yhat'])
        plot_revenue_with_error(train_forecast['ds'],train_data['y'],train_forecast['ds'],train_forecast['yhat'],[0,150])
        st.write(f"TRAIN_MAPE: {(train_mape)}")
        st.write(f'VALIDATION_MAPE: {val_mape}')
    
    st.subheader('Forecast with Changepoints ')
    col21,col22 = st.columns(2)
   
    with col21:
        fig2 = model.plot(forecast)  #2nd graph with changepoints
        a = add_changepoints_to_plot(fig2.gca(), model, forecast)
        st.pyplot(fig2)
       # st.write(f"No. of CHANGEPOITNS found between 2021 and 2024: {(len(model.changepoints))}")
        #st.write(f"**After applying Hyperparameter Tuning,we get changepoint_prior scale:  0.01  ** ")
    
    st.subheader('Forecast with TUNING ')
    col23,col24 = st.columns(2)
    
    with col23:
        m3_changepoints = pd.date_range('2023-02-10', '2023-12-01', periods=10).date.tolist()
        m3 = Prophet(changepoints=m3_changepoints, changepoint_prior_scale=0.97)
        m3 = m3.fit(train_data)
        future3 = m3.make_future_dataframe(periods=21)
        forecast3 = m3.predict(future3)
        fig3  = m3.plot(forecast3) #3rd graph without  changepoint
        st.pyplot(fig3)
        train_forecast = m3.predict(train_data[['ds']])
        val_forecast = m3.predict(test_data_for_21_days[['ds']])
        train_mape = mean_absolute_percentage_error(train_data['y'], train_forecast['yhat'])
        val_mape = mean_absolute_percentage_error(test_data_for_21_days['y'], val_forecast['yhat'].tail(21))
        plot_revenue_with_error(train_forecast['ds'],train_data['y'],train_forecast['ds'],train_forecast['yhat'],[0,150])
        st.write(f'Training MAPE: {train_mape}')
        st.write(f'Validation_MAPE: {val_mape}')


    #PROPHET FORECAST FOR INDIVIDUAL REVENUE
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
    data = pd.concat([data4,data5],ignore_index=True)
    data = data[['Business Date','Individual Revenue']]
    data.columns = ['ds','y'] 
    data['ds'] = pd.to_datetime(data['ds'])
    data = data.drop_duplicates()  
    data = data.sort_values(by='ds')
    train_data = data.iloc[520:844]
    test_data_for_21_days = data.iloc[844:865]
    
 
    st.subheader('INDIVIDUAL REVENUE')
    st.subheader('Forecast without Tuning ')
    col25,col26 = st.columns(2)
    with col25:
        model = Prophet()
        model.fit(train_data)
        future = model.make_future_dataframe(periods=21)
        forecast = model.predict(future)
        fig1 = model.plot(forecast)
        st.pyplot(fig1)
        train_forecast = model.predict(train_data[['ds']])
        val_forecast = model.predict(test_data_for_21_days[['ds']])
        train_mape = mean_absolute_percentage_error(train_data['y'], train_forecast['yhat'])
        val_mape = mean_absolute_percentage_error(test_data_for_21_days['y'], val_forecast['yhat'])
        plot_revenue_with_error(train_forecast['ds'],train_data['y'],train_forecast['ds'],train_forecast['yhat'],[0,2000000])
        st.write(f"TRAIN_MAPE: {(train_mape)}")
        st.write(f'VALIDATION_MAPE: {val_mape}')
    
    st.subheader('Forecast with Changepoints ')
    col27,col28 = st.columns(2)
   
    with col27:
        fig2 = model.plot(forecast)  #2nd graph with changepoints
        a = add_changepoints_to_plot(fig2.gca(), model, forecast)
        st.pyplot(fig2)
      #  st.write(f"No. of CHANGEPOITNS found between 2021 and 2024: {(len(model.changepoints))}")
        #st.write(f"**After applying Hyperparameter Tuning,we get changepoint_prior scale:  0.01  ** ")
    
    st.subheader('Forecast with TUNING ')
    col29,col30 = st.columns(2)
    with col29:
        m3_changepoints = pd.date_range('2023-02-05', '2023-12-01', periods=10).date.tolist()
        m3 = Prophet(changepoints=m3_changepoints, changepoint_prior_scale=0.95)
        m3 = m3.fit(train_data)
        future3 = m3.make_future_dataframe(periods=21)
        forecast3 = m3.predict(future3)
        fig3  = m3.plot(forecast3) #3rd graph without  changepoint
        st.pyplot(fig3)
        train_forecast = m3.predict(train_data[['ds']])
        val_forecast = m3.predict(test_data_for_21_days[['ds']])
        train_mape = mean_absolute_percentage_error(train_data['y'], train_forecast['yhat'])
        val_mape = mean_absolute_percentage_error(test_data_for_21_days['y'], val_forecast['yhat'].tail(21))
        plot_revenue_with_error(train_forecast['ds'],train_data['y'],train_forecast['ds'],train_forecast['yhat'],[0,2000000])
        st.write(f'Training MAPE: {train_mape}')
        st.write(f'Validation_MAPE: {val_mape}')


if __name__ == '__main__':
    main()














