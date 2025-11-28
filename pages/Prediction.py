import base64
import os
from io import BytesIO
#from streamlit_extras.switch_page_button import switch_page
from statistics import mean
import streamlit as st
import pandas as pd
import plotly.express as px
import calendar
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
    selected_page = selected_page or "Prediction"
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
            <a style="color: {'red' if selected_page == 'Trend' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'Trend' else 'none'}" href="/trend" target="_self">Trend</a>
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
  #  "/Prediction": "Prediction",
    "/upload": "Upload",
    "/market": "market",
    "/Prediction": "Prediction",
      "/Trend": "Trend",
    #  "/Yearly": "Yearly"
}
selected_page = url_to_page.get(url_path)
custom_top_bar(selected_page)
# -----------------------------------------------
def plot_graph_with_error(actual_dates, actual_revenue, predicted_revenue, range1):
    # Calculate day-to-day APE
    daily_ape = calculate_day_to_day_ape(actual_revenue, predicted_revenue)

    # Create figure and primary axis
    fig = go.Figure()
    
    # Plot actual revenue
    fig.add_trace(go.Scatter(x=actual_dates, y=actual_revenue, mode='lines+markers',
                             name='Actual', line=dict(color='blue')))
    #yaxis=dict(title='Revenue (in Lakhs)', range=[100000,2000000])
    # Plot predicted revenue
    fig.add_trace(go.Scatter(x=actual_dates, y=predicted_revenue, mode='lines+markers',
                             name='Predicted', line=dict(color='red')))
    
    # Add secondary axis for the error rate
    fig.add_trace(go.Scatter(x=actual_dates, y=daily_ape, mode='lines+markers',
                             name='Error Rate (%)', yaxis='y2', line=dict(color='green')))
    
    # Layout adjustments
    fig.update_layout(
        
        xaxis_title='Date',
        #yaxis=dict(title='Revenue'),
        yaxis=dict(title='Revenue (in Lakhs)', range=range1),
        yaxis2=dict(title='Error Rate (%)', overlaying='y', side='right', range=[0, 100]),  # Secondary y-axis for error rate
        legend=dict(x=0.01, y=0.99, bordercolor='Black', borderwidth=1)
    )
    
    # Plot the figure in Streamlit
    st.plotly_chart(fig)

def calculate_day_to_day_ape(actual, predicted):
    actual, predicted = np.array(actual), np.array(predicted)
    return np.abs((actual - predicted) / actual) * 100
# ---------------------------------------------------------------------
def calculate_mape(actual, predicted):
    actual, predicted = np.array(actual), np.array(predicted)
    mask = actual != 0
    mape = (np.abs(actual - predicted) / actual)[mask].mean() * 100
    return mape

def plot_month_data_rooms(merged_data):
    # Plotting using Plotly
    fig = go.Figure()
    
    # Plotting bars for 2023
    fig.add_trace(go.Bar(
        x=merged_data['Month'],
        y=merged_data['y'],
        name='2023',
        marker_color='skyblue'
    ))
    
    # Update layout for better interactivity
    fig.update_layout(
        barmode='group',  # Display bars in groups
        title='Entities generated for Each Month (2023)',
        xaxis=dict(title='Month'),
        yaxis=dict(title='Total Entities'),
        hovermode='x',
        showlegend=True,
        legend_title='Legend',
        font=dict(family='Arial', size=14),
        height=600,  # Adjust the height of the plot
        width=1000,   # Adjust the width of the plot
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    # Show the plot in Streamlit
    st.plotly_chart(fig)
# ---------------------------------------------------------------------
def calculate_day_to_day_ape(actual, predicted):
    actual, predicted = np.array(actual), np.array(predicted)
    return np.abs((actual - predicted) / actual) * 100
# ---------------------------------------------------------------------
def calculate_mape(actual, predicted):
    actual, predicted = np.array(actual), np.array(predicted)
    mask = actual != 0
    mape = (np.abs(actual - predicted) / actual)[mask].mean() * 100
    return mape
#---------------------------------------------------------------------
def plot_month_data(merged_data):
    # Plotting using Plotly
    fig = go.Figure()
    
    # Plotting bars for 2022
    fig.add_trace(go.Bar(
    x=merged_data['Month'],
    y=merged_data['y_2022'],
    name='2022',
    marker_color='skyblue'
    ))
    
    # Plotting bars for 2023
    fig.add_trace(go.Bar(
    x= merged_data['Month'],
    y= merged_data['y_2023'],
    name='2023',
    marker_color='orange'
    ))
    
    # Update layout for better interactivity
    fig.update_layout(
    barmode='group',  # Display bars in groups
    title='Entities generated for Each Month (2022-2023)',
    xaxis=dict(title='Month'),
    yaxis=dict(title='Total Entities '),
    hovermode='x',
    showlegend=True,
    legend_title='Legend',
    font=dict(family='Arial', size=14),
    height=600,  # Adjust the height of the plot
    width=1000,   # Adjust the width of the plot
    margin=dict(l=20, r=20, t=40, b=20),
    )
    
    # Show the plot
    st.plotly_chart(fig)

# ---------------------------------------------------------------------
def plot_month_data_rooms(merged_data):
    # Plotting using Plotly
    fig = go.Figure()
    
    # Plotting bars for 2023
    fig.add_trace(go.Bar(
        x=merged_data['Month'],
        y=merged_data['y'],
        name='2023',
        marker_color='skyblue'
    ))
    
    # Update layout for better interactivity
    fig.update_layout(
        barmode='group',  # Display bars in groups
        title='Entities generated for Each Month (2023)',
        xaxis=dict(title='Month'),
        yaxis=dict(title='Total Entities'),
        hovermode='x',
        showlegend=True,
        legend_title='Legend',
        font=dict(family='Arial', size=14),
        height=600,  # Adjust the height of the plot
        width=1000,   # Adjust the width of the plot
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    # Show the plot in Streamlit
    st.plotly_chart(fig)
# ---------------------------------------------------------------------
def evaluation_metrics(actual,predicted):
    tp_for_10_days = 0
    tn_for_10_days = 0
    fp_for_10_days = 0
    fn_for_10_days = 0
    for i,j in zip(actual,predicted):
        c = i-j
        c = abs(i-j)
        c = c*100/i
        c  = 100-c
        c= int(c)
        if i <j:
            if c>80 and c<100:
                tp_for_10_days +=1
            elif c<80:
                fp_for_10_days+=1
        elif  i>j:
            if  c>80 and c<100:
                tn_for_10_days +=1
            elif c<80:
                fn_for_10_days+=1

    sensitivity = tp_for_10_days / (tp_for_10_days + fn_for_10_days) if (tp_for_10_days + fn_for_10_days) >0 else 0
    specificity = tn_for_10_days / (tn_for_10_days + fp_for_10_days) if (tn_for_10_days + fp_for_10_days) > 0 else 0
    precision = tp_for_10_days / (tp_for_10_days + fp_for_10_days) if (tp_for_10_days + fp_for_10_days) > 0 else 0
    
    return sensitivity,specificity,precision





def aggregate_accuracy(df, freq):
    # Ensure 'ds' is a column. If not, and if it's the index, reset it.
    if 'Date' not in df.columns:
        if df.index.name == 'Date':
            df.reset_index(inplace=True)
        else:
            raise KeyError("'Date' column is missing in the input DataFrame. Please include it.")
    
    # Set 'ds' as the index for resampling
    df.set_index('Date', inplace=True)
    df_agg = df.resample(freq).sum()
    df_agg['Accuracy'] = 1 - np.abs((df_agg['Actual'] - df_agg['Predicted']) / df_agg['Actual'])
    df_agg['Accuracy'] = (df_agg['Accuracy'].clip(lower=0) * 100).round(2)
    return df_agg.reset_index()


#FOR MONTHLY VIEW AND DAILY VIEW

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

#FOR FETCHING DATA ACCURACY
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
    #--------------------------------------
    
    data1 =  data4[['Business Date','Room Revenue','Rooms Sold']]
    data2 = data5[['Business Date','Room Revenue','Rooms Sold','Arrival Rooms','Individual Revenue','Individual Confirm']]
    data = pd.concat([data1,data2],ignore_index=True)
    print(len(data))
    print(data)
    #---------------------------------------------------------------------------
    # st.subheader("Select Date Range for Analysis")
    # date_range = st.date_input("Select Date Range", [])
    # if len(date_range) == 2:
    #     start_date, end_date = date_range
    # else:
    #     start_date, end_date = None, None  

    # if start_date and end_date:
    #     data['Business Date'] = pd.to_datetime(data['Business Date'])
    #     start_date = pd.to_datetime(start_date)
    #     end_date = pd.to_datetime(end_date)

    #     # Filter data based on selected date range
    #     filtered_data = data[(data['Business Date'] >= start_date) & (data['Business Date'] <= end_date)]

    #     # Show filtered data or perform further analysis
    #     st.write("Filtered Data", filtered_data)  # Placeholder for actual data handling
    # else:
    #     st.write("Please select a start and end date to filter the data.")
   
    #YEARLY, MONTH, DAILY AND WEEKLY VIEW
    st.subheader("Prediction")
    options = ["", "Room Revenue", "Room Sold", "Arrival Room", "Individual Confirm", "Individual Revenue"]
    view_option = st.selectbox("Select Feature", options, index=0)  # Set the first item as default
    #view_option = st.selectbox("Select View", ['Room Revenue','Room Sold','Arrival Room','Individual Confirm','Individual Revenue'])
 
   
    #DAY TO DAY REVENUE
    if view_option == 'Room Revenue':
        import revenue as rev
        st.header('Daily Revenue')
        result_df, merged_data = rev.prophet()
        result_df = result_df.rename(columns={'ds': 'Date','y': 'Actual','yhat': 'Predicted','Daily Accuracy': 'Accuracy'})
        result_df['Predicted'] = result_df['Predicted'].round()
        result_df['Accuracy'] = (result_df['Accuracy']*100).round()
        st.dataframe(result_df[['Date','Actual','Predicted','Accuracy']], hide_index=True)
        plot_graph_with_error(result_df['Date'],result_df['Actual'],result_df['Predicted'],(0,2000000))
        st.write(f"Accuracy :{round(mean(result_df['Accuracy']))}%")
        st.write(f"MAE:{round(mean_absolute_error(result_df['Actual'],result_df['Predicted']))}")
        st.write(f"MAPE:{round(calculate_mape(result_df['Actual'],result_df['Predicted']))}%")
        st.write(f"MSE:{round(mean_squared_error(result_df['Actual'],result_df['Predicted']))}%")
        st.write(f"Sensitivity: {evaluation_metrics(result_df['Actual'],result_df['Predicted'])[0]}")
        st.write(f"Specificity: {evaluation_metrics(result_df['Actual'],result_df['Predicted'])[1]}")
        st.write(f"Precision: {evaluation_metrics(result_df['Actual'],result_df['Predicted'])[2]}")
        #plot_month_data(merged_data)


        #WEEKLY REVENUE
        st.header('Weekly Revenue')
        weekly_data = aggregate_accuracy(result_df, 'W')
        st.dataframe(weekly_data[['Date', 'Actual', 'Predicted', 'Accuracy']], hide_index=True)
        plot_graph_with_error(weekly_data['Date'], weekly_data['Actual'], weekly_data['Predicted'],(0, 16000000))
        st.write(f"Accuracy :{round(mean(weekly_data['Accuracy']))}%")
        st.write(f"MAE:{round(mean_absolute_error(weekly_data['Actual'],weekly_data['Predicted']))}")
        st.write(f"MAPE:{round(calculate_mape(weekly_data['Actual'],weekly_data['Predicted']))}%")
        st.write(f"MSE:{round(mean_squared_error(weekly_data['Actual'],weekly_data['Predicted']))}%")
        st.write(f"Sensitivity: {evaluation_metrics(weekly_data['Actual'],weekly_data['Predicted'])[0]}")
        st.write(f"Specificity: {evaluation_metrics(weekly_data['Actual'],weekly_data['Predicted'])[1]}")
        st.write(f"Precision: {evaluation_metrics(weekly_data['Actual'],weekly_data['Predicted'])[2]}")
        


        #MONTHLY REVENUE
        st.header('Monthly Revenue')
        monthly_data = aggregate_accuracy(result_df, 'M')
        st.dataframe(monthly_data[['Date', 'Actual', 'Predicted', 'Accuracy']], hide_index=True)
        plot_graph_with_error(monthly_data['Date'], monthly_data['Actual'], monthly_data['Predicted'],(0, 60000000))
        st.write(f"Accuracy :{round(mean(monthly_data['Accuracy']))}%")
        st.write(f"MAE:{round(mean_absolute_error(monthly_data['Actual'],monthly_data['Predicted']))}")
        st.write(f"MAPE:{round(calculate_mape(monthly_data['Actual'],monthly_data['Predicted']))}%")
        st.write(f"MSE:{round(mean_squared_error(monthly_data['Actual'],monthly_data['Predicted']))}%")
        st.write(f"Sensitivity: {evaluation_metrics(monthly_data['Actual'],monthly_data['Predicted'])[0]}")
        st.write(f"Specificity: {evaluation_metrics(monthly_data['Actual'],monthly_data['Predicted'])[1]}")
        st.write(f"Precision: {evaluation_metrics(monthly_data['Actual'],monthly_data['Predicted'])[2]}")

        #YEARLY REVENUE
        st.header('Yearly Revenue')
        yearly_data = aggregate_accuracy(result_df, 'Y')
        st.dataframe(yearly_data[['Date', 'Actual', 'Predicted', 'Accuracy']], hide_index=True)
        plot_graph_with_error(yearly_data['Date'], yearly_data['Actual'], yearly_data['Predicted'],(0, 150000000))
        st.write(f"Accuracy :{round(mean(yearly_data['Accuracy']))}%")
        st.write(f"MAE:{round(mean_absolute_error(yearly_data['Actual'],yearly_data['Predicted']))}")
        st.write(f"MAPE:{round(calculate_mape(yearly_data['Actual'],yearly_data['Predicted']))}%")
        st.write(f"MSE:{round(mean_squared_error(yearly_data['Actual'],yearly_data['Predicted']))}%")
        st.write(f"Sensitivity: {evaluation_metrics(yearly_data['Actual'],yearly_data['Predicted'])[0]}")
        st.write(f"Specificity: {evaluation_metrics(yearly_data['Actual'],yearly_data['Predicted'])[1]}")
        st.write(f"Precision: {evaluation_metrics(yearly_data['Actual'],yearly_data['Predicted'])[2]}")

    elif view_option == 'Room Sold':
        #DAY TO DAY ROOM SOLD
        import room_sold as room 
        st.header('DAY TO DAY ROOM SOLD')
        result_df, merged_data = room.prophet()
        result_df = result_df.rename(columns={'ds': 'Date','y': 'Actual','yhat': 'Predicted','Daily Accuracy': 'Accuracy'})
        result_df['Predicted'] = result_df['Predicted'].round()
        result_df['Accuracy'] = (result_df['Accuracy']*100).round()
        st.dataframe(result_df[['Date','Actual','Predicted','Accuracy']], hide_index=True)
        plot_graph_with_error(result_df['Date'],result_df['Actual'],result_df['Predicted'],(0,150))
        st.write(f"Accuracy :{round(mean(result_df['Accuracy']))}%")
        st.write(f"MAE:{round(mean_absolute_error(result_df['Actual'],result_df['Predicted']))}")
        st.write(f"MAPE:{round(calculate_mape(result_df['Actual'],result_df['Predicted']))}%")
        st.write(f"MSE:{round(mean_squared_error(result_df['Actual'],result_df['Predicted']))}%")
        st.write(f"Sensitivity: {evaluation_metrics(result_df['Actual'],result_df['Predicted'])[0]}")
        st.write(f"Specificity: {evaluation_metrics(result_df['Actual'],result_df['Predicted'])[1]}")
        st.write(f"Precision: {evaluation_metrics(result_df['Actual'],result_df['Predicted'])[2]}")

        #WEEKLY ROOM SOLD
        st.header('Weekly ROOM SOLD')
        weekly_data = aggregate_accuracy(result_df, 'W')
        st.dataframe(weekly_data[['Date', 'Actual', 'Predicted', 'Accuracy']], hide_index=True)
        plot_graph_with_error(weekly_data['Date'], weekly_data['Actual'], weekly_data['Predicted'],(0, 1200))
        st.write(f"Accuracy :{round(mean(weekly_data['Accuracy']))}%")
        st.write(f"MAE:{round(mean_absolute_error(weekly_data['Actual'],weekly_data['Predicted']))}")
        st.write(f"MAPE:{round(calculate_mape(weekly_data['Actual'],weekly_data['Predicted']))}%")
        st.write(f"MSE:{round(mean_squared_error(weekly_data['Actual'],weekly_data['Predicted']))}%")
        st.write(f"Sensitivity: {evaluation_metrics(weekly_data['Actual'],weekly_data['Predicted'])[0]}")
        st.write(f"Specificity: {evaluation_metrics(weekly_data['Actual'],weekly_data['Predicted'])[1]}")
        st.write(f"Precision: {evaluation_metrics(weekly_data['Actual'],weekly_data['Predicted'])[2]}")
      

        #MONTHLY ROOM SOLD
        st.header('Monthly ROOM SOLD')
        monthly_data = aggregate_accuracy(result_df, 'M')
        st.dataframe(monthly_data[['Date', 'Actual', 'Predicted', 'Accuracy']], hide_index=True)
        plot_graph_with_error(monthly_data['Date'], monthly_data['Actual'], monthly_data['Predicted'],(0, 5000))
        st.write(f"Accuracy :{round(mean(monthly_data['Accuracy']))}%")
        st.write(f"MAE:{round(mean_absolute_error(monthly_data['Actual'],monthly_data['Predicted']))}")
        st.write(f"MAPE:{round(calculate_mape(monthly_data['Actual'],monthly_data['Predicted']))}%")
        st.write(f"MSE:{round(mean_squared_error(monthly_data['Actual'],monthly_data['Predicted']))}%")
        st.write(f"Sensitivity: {evaluation_metrics(monthly_data['Actual'],monthly_data['Predicted'])[0]}")
        st.write(f"Specificity: {evaluation_metrics(monthly_data['Actual'],monthly_data['Predicted'])[1]}")
        st.write(f"Precision: {evaluation_metrics(monthly_data['Actual'],monthly_data['Predicted'])[2]}")


        #YEARLY ROOM SOLD
        st.header('Yearly ROOM SOLD')
        yearly_data = aggregate_accuracy(result_df, 'Y')
        st.dataframe(yearly_data[['Date', 'Actual', 'Predicted', 'Accuracy']], hide_index=True)
        plot_graph_with_error(yearly_data['Date'], yearly_data['Actual'], yearly_data['Predicted'],(0, 12000))
        st.write(f"Accuracy :{round(mean(yearly_data['Accuracy']))}%")
        st.write(f"MAE:{round(mean_absolute_error(yearly_data['Actual'],yearly_data['Predicted']))}")
        st.write(f"MAPE:{round(calculate_mape(yearly_data['Actual'],yearly_data['Predicted']))}%")
        st.write(f"MSE:{round(mean_squared_error(yearly_data['Actual'],yearly_data['Predicted']))}%")
        st.write(f"Sensitivity: {evaluation_metrics(yearly_data['Actual'],yearly_data['Predicted'])[0]}")
        st.write(f"Specificity: {evaluation_metrics(yearly_data['Actual'],yearly_data['Predicted'])[1]}")
        st.write(f"Precision: {evaluation_metrics(yearly_data['Actual'],yearly_data['Predicted'])[2]}")
       

    elif view_option == "Arrival Room":
        #DAY TO DAY ARRIVAL ROOM
        import Arrival as arriv
        st.header('DAY TO DAY ARRIVAL ROOM')
        result_df, merged_data = arriv.prophet()
        result_df = result_df.rename(columns={'ds': 'Date','y': 'Actual','yhat': 'Predicted','Daily Accuracy': 'Accuracy'})
        result_df['Predicted'] = result_df['Predicted'].round()
        result_df['Accuracy'] = (result_df['Accuracy']*100).round()
        st.dataframe(result_df[['Date','Actual','Predicted','Accuracy']], hide_index=True)
        plot_graph_with_error(result_df['Date'],result_df['Actual'],result_df['Predicted'],(0,150))
        st.write(f"Accuracy :{round(mean(result_df['Accuracy']))}%")
        st.write(f"MAE:{round(mean_absolute_error(result_df['Actual'],result_df['Predicted']))}")
        st.write(f"MAPE:{round(calculate_mape(result_df['Actual'],result_df['Predicted']))}%")
        st.write(f"MSE:{round(mean_squared_error(result_df['Actual'],result_df['Predicted']))}%")
        st.write(f"Sensitivity: {evaluation_metrics(result_df['Actual'],result_df['Predicted'])[0]}")
        st.write(f"Specificity: {evaluation_metrics(result_df['Actual'],result_df['Predicted'])[1]}")
        st.write(f"Precision: {evaluation_metrics(result_df['Actual'],result_df['Predicted'])[2]}")
       

        #WEEKLY ARRIVAL ROOM
        st.header('Weekly ARRIVAL ROOM')
        weekly_data = aggregate_accuracy(result_df, 'W')
        st.dataframe(weekly_data[['Date', 'Actual', 'Predicted', 'Accuracy']], hide_index=True)
        plot_graph_with_error(weekly_data['Date'], weekly_data['Actual'], weekly_data['Predicted'],(0, 1200))
        st.write(f"Accuracy :{round(mean(weekly_data['Accuracy']))}%")
        st.write(f"MAE:{round(mean_absolute_error(weekly_data['Actual'],weekly_data['Predicted']))}")
        st.write(f"MAPE:{round(calculate_mape(weekly_data['Actual'],weekly_data['Predicted']))}%")
        st.write(f"MSE:{round(mean_squared_error(weekly_data['Actual'],weekly_data['Predicted']))}%")
        st.write(f"Sensitivity: {evaluation_metrics(weekly_data['Actual'],weekly_data['Predicted'])[0]}")
        st.write(f"Specificity: {evaluation_metrics(weekly_data['Actual'],weekly_data['Predicted'])[1]}")
        st.write(f"Precision: {evaluation_metrics(weekly_data['Actual'],weekly_data['Predicted'])[2]}")
      

        #MONTHLY ARRIVAL ROOM
        st.header('Monthly ARRIVAL ROOM')
        monthly_data = aggregate_accuracy(result_df, 'M')
        st.dataframe(monthly_data[['Date', 'Actual', 'Predicted', 'Accuracy']], hide_index=True)
        plot_graph_with_error(monthly_data['Date'], monthly_data['Actual'], monthly_data['Predicted'],(0, 5000))
        st.write(f"Accuracy :{round(mean(monthly_data['Accuracy']))}%")
        st.write(f"MAE:{round(mean_absolute_error(monthly_data['Actual'],monthly_data['Predicted']))}")
        st.write(f"MAPE:{round(calculate_mape(monthly_data['Actual'],monthly_data['Predicted']))}%")
        st.write(f"MSE:{round(mean_squared_error(monthly_data['Actual'],monthly_data['Predicted']))}%")
        st.write(f"Sensitivity: {evaluation_metrics(monthly_data['Actual'],monthly_data['Predicted'])[0]}")
        st.write(f"Specificity: {evaluation_metrics(monthly_data['Actual'],monthly_data['Predicted'])[1]}")
        st.write(f"Precision: {evaluation_metrics(monthly_data['Actual'],monthly_data['Predicted'])[2]}")


        #YEARLY ARRIVAL ROOM
        st.header('Yearly ARRIVAL ROOM')
        yearly_data = aggregate_accuracy(result_df, 'Y')
        st.dataframe(yearly_data[['Date', 'Actual', 'Predicted', 'Accuracy']], hide_index=True)
        plot_graph_with_error(yearly_data['Date'], yearly_data['Actual'], yearly_data['Predicted'],(0, 12000))
        st.write(f"Accuracy :{round(mean(yearly_data['Accuracy']))}%")
        st.write(f"MAE:{round(mean_absolute_error(yearly_data['Actual'],yearly_data['Predicted']))}")
        st.write(f"MAPE:{round(calculate_mape(yearly_data['Actual'],yearly_data['Predicted']))}%")
        st.write(f"MSE:{round(mean_squared_error(yearly_data['Actual'],yearly_data['Predicted']))}%")
        st.write(f"Sensitivity: {evaluation_metrics(yearly_data['Actual'],yearly_data['Predicted'])[0]}")
        st.write(f"Specificity: {evaluation_metrics(yearly_data['Actual'],yearly_data['Predicted'])[1]}")
        st.write(f"Precision: {evaluation_metrics(yearly_data['Actual'],yearly_data['Predicted'])[2]}")

    elif view_option == "Individual Revenue":
        #DAY TO DAY Individual Revenue
        import Individual_R as ir
        st.header('DAY TO DAY Individual Revenue')
        result_df, merged_data = ir.prophet()
        result_df = result_df.rename(columns={'ds': 'Date','y': 'Actual','yhat': 'Predicted','Daily Accuracy': 'Accuracy'})
        result_df['Predicted'] = result_df['Predicted'].round()
        result_df['Accuracy'] = (result_df['Accuracy']*100).round()
        st.dataframe(result_df[['Date','Actual','Predicted','Accuracy']], hide_index=True)
        plot_graph_with_error(result_df['Date'],result_df['Actual'],result_df['Predicted'],(0,2000000))
        st.write(f"Accuracy :{round(mean(result_df['Accuracy']))}%")
        st.write(f"MAE:{round(mean_absolute_error(result_df['Actual'],result_df['Predicted']))}")
        st.write(f"MAPE:{round(calculate_mape(result_df['Actual'],result_df['Predicted']))}%")
        st.write(f"MSE:{round(mean_squared_error(result_df['Actual'],result_df['Predicted']))}%")
        st.write(f"Sensitivity: {evaluation_metrics(result_df['Actual'],result_df['Predicted'])[0]}")
        st.write(f"Specificity: {evaluation_metrics(result_df['Actual'],result_df['Predicted'])[1]}")
        st.write(f"Precision: {evaluation_metrics(result_df['Actual'],result_df['Predicted'])[2]}")
        

        #WEEKLY Individual Revenue
        st.header('Weekly Individual Revenue')
        weekly_data = aggregate_accuracy(result_df, 'W')
        st.dataframe(weekly_data[['Date', 'Actual', 'Predicted', 'Accuracy']], hide_index=True)
        plot_graph_with_error(weekly_data['Date'], weekly_data['Actual'], weekly_data['Predicted'],(0, 16000000))
        st.write(f"Accuracy :{round(mean(weekly_data['Accuracy']))}%")
        st.write(f"MAE:{round(mean_absolute_error(weekly_data['Actual'],weekly_data['Predicted']))}")
        st.write(f"MAPE:{round(calculate_mape(weekly_data['Actual'],weekly_data['Predicted']))}%")
        st.write(f"MSE:{round(mean_squared_error(weekly_data['Actual'],weekly_data['Predicted']))}%")
        st.write(f"Sensitivity: {evaluation_metrics(weekly_data['Actual'],weekly_data['Predicted'])[0]}")
        st.write(f"Specificity: {evaluation_metrics(weekly_data['Actual'],weekly_data['Predicted'])[1]}")
        st.write(f"Precision: {evaluation_metrics(weekly_data['Actual'],weekly_data['Predicted'])[2]}")

        #MONTHLY Individual Revenue
        st.header('Monthly Individual Revenue')
        monthly_data = aggregate_accuracy(result_df, 'M')
        st.dataframe(monthly_data[['Date', 'Actual', 'Predicted', 'Accuracy']], hide_index=True)
        plot_graph_with_error(monthly_data['Date'], monthly_data['Actual'], monthly_data['Predicted'],(0, 60000000))
        st.write(f"Accuracy :{round(mean(monthly_data['Accuracy']))}%")
        st.write(f"MAE:{round(mean_absolute_error(monthly_data['Actual'],monthly_data['Predicted']))}")
        st.write(f"MAPE:{round(calculate_mape(monthly_data['Actual'],monthly_data['Predicted']))}%")
        st.write(f"MSE:{round(mean_squared_error(monthly_data['Actual'],monthly_data['Predicted']))}%")
        st.write(f"Sensitivity: {evaluation_metrics(monthly_data['Actual'],monthly_data['Predicted'])[0]}")
        st.write(f"Specificity: {evaluation_metrics(monthly_data['Actual'],monthly_data['Predicted'])[1]}")
        st.write(f"Precision: {evaluation_metrics(monthly_data['Actual'],monthly_data['Predicted'])[2]}")


        

        #YEARLY Individual Revenue
        st.header('Yearly Individual Revenue')
        yearly_data = aggregate_accuracy(result_df, 'Y')
        st.dataframe(yearly_data[['Date', 'Actual', 'Predicted', 'Accuracy']], hide_index=True)
        plot_graph_with_error(yearly_data['Date'], yearly_data['Actual'], yearly_data['Predicted'],(0, 150000000))
        st.write(f"Accuracy :{round(mean(yearly_data['Accuracy']))}%")
        st.write(f"MAE:{round(mean_absolute_error(yearly_data['Actual'],yearly_data['Predicted']))}")
        st.write(f"MAPE:{round(calculate_mape(yearly_data['Actual'],yearly_data['Predicted']))}%")
        st.write(f"MSE:{round(mean_squared_error(yearly_data['Actual'],yearly_data['Predicted']))}%")
        st.write(f"Sensitivity: {evaluation_metrics(yearly_data['Actual'],yearly_data['Predicted'])[0]}")
        st.write(f"Specificity: {evaluation_metrics(yearly_data['Actual'],yearly_data['Predicted'])[1]}")
        st.write(f"Precision: {evaluation_metrics(yearly_data['Actual'],yearly_data['Predicted'])[2]}")

    elif view_option == "Individual Confirm":
        #DAY TO DAY Individual Confirm
        import Confirm as ir
        st.header('DAY TO DAY Individual Confirm')
        result_df, merged_data = ir.prophet()
        result_df = result_df.rename(columns={'ds': 'Date','y': 'Actual','yhat': 'Predicted','Daily Accuracy': 'Accuracy'})
        result_df['Predicted'] = result_df['Predicted'].round()
        result_df['Accuracy'] = (result_df['Accuracy']*100).round()
        st.dataframe(result_df[['Date','Actual','Predicted','Accuracy']], hide_index=True)
        plot_graph_with_error(result_df['Date'],result_df['Actual'],result_df['Predicted'],(0,150))
        st.write(f"Accuracy :{round(mean(result_df['Accuracy']))}%")
        st.write(f"MAE:{round(mean_absolute_error(result_df['Actual'],result_df['Predicted']))}")
        st.write(f"MAPE:{round(calculate_mape(result_df['Actual'],result_df['Predicted']))}%")
        st.write(f"MSE:{round(mean_squared_error(result_df['Actual'],result_df['Predicted']))}%")
        st.write(f"Sensitivity: {evaluation_metrics(result_df['Actual'],result_df['Predicted'])[0]}")
        st.write(f"Specificity: {evaluation_metrics(result_df['Actual'],result_df['Predicted'])[1]}")
        st.write(f"Precision: {evaluation_metrics(result_df['Actual'],result_df['Predicted'])[2]}")

        #WEEKLY Individual Confirm
        st.header('Weekly Individual Confirm')
        weekly_data = aggregate_accuracy(result_df, 'W')
        st.dataframe(weekly_data[['Date', 'Actual', 'Predicted', 'Accuracy']], hide_index=True)
        plot_graph_with_error(weekly_data['Date'], weekly_data['Actual'], weekly_data['Predicted'],(0, 1200))
        st.write(f"Accuracy :{round(mean(weekly_data['Accuracy']))}%")
        st.write(f"MAE:{round(mean_absolute_error(weekly_data['Actual'],weekly_data['Predicted']))}")
        st.write(f"MAPE:{round(calculate_mape(weekly_data['Actual'],weekly_data['Predicted']))}%")
        st.write(f"MSE:{round(mean_squared_error(weekly_data['Actual'],weekly_data['Predicted']))}%")
        st.write(f"Sensitivity: {evaluation_metrics(weekly_data['Actual'],weekly_data['Predicted'])[0]}")
        st.write(f"Specificity: {evaluation_metrics(weekly_data['Actual'],weekly_data['Predicted'])[1]}")
        st.write(f"Precision: {evaluation_metrics(weekly_data['Actual'],weekly_data['Predicted'])[2]}")
      

        #MONTHLY Individual Confirm
        st.header('Monthly Individual Confirm')
        monthly_data = aggregate_accuracy(result_df, 'M')
        st.dataframe(monthly_data[['Date', 'Actual', 'Predicted', 'Accuracy']], hide_index=True)
        plot_graph_with_error(monthly_data['Date'], monthly_data['Actual'], monthly_data['Predicted'],(0, 5000))
        st.write(f"Accuracy :{round(mean(monthly_data['Accuracy']))}%")
        st.write(f"MAE:{round(mean_absolute_error(monthly_data['Actual'],monthly_data['Predicted']))}")
        st.write(f"MAPE:{round(calculate_mape(monthly_data['Actual'],monthly_data['Predicted']))}%")
        st.write(f"MSE:{round(mean_squared_error(monthly_data['Actual'],monthly_data['Predicted']))}%")
        st.write(f"Sensitivity: {evaluation_metrics(monthly_data['Actual'],monthly_data['Predicted'])[0]}")
        st.write(f"Specificity: {evaluation_metrics(monthly_data['Actual'],monthly_data['Predicted'])[1]}")
        st.write(f"Precision: {evaluation_metrics(monthly_data['Actual'],monthly_data['Predicted'])[2]}")

        

        #YEARLY Individual Confirm
        st.header('Yearly Individual Confirm')
        yearly_data = aggregate_accuracy(result_df, 'Y')
        st.dataframe(yearly_data[['Date', 'Actual', 'Predicted', 'Accuracy']], hide_index=True)
        plot_graph_with_error(yearly_data['Date'], yearly_data['Actual'], yearly_data['Predicted'],(0, 12000))
        st.write(f"Accuracy :{round(mean(yearly_data['Accuracy']))}%")
        st.write(f"MAE:{round(mean_absolute_error(yearly_data['Actual'],yearly_data['Predicted']))}")
        st.write(f"MAPE:{round(calculate_mape(yearly_data['Actual'],yearly_data['Predicted']))}%")
        st.write(f"MSE:{round(mean_squared_error(yearly_data['Actual'],yearly_data['Predicted']))}%")
        st.write(f"Sensitivity: {evaluation_metrics(yearly_data['Actual'],yearly_data['Predicted'])[0]}")
        st.write(f"Specificity: {evaluation_metrics(yearly_data['Actual'],yearly_data['Predicted'])[1]}")
        st.write(f"Precision: {evaluation_metrics(yearly_data['Actual'],yearly_data['Predicted'])[2]}")
        




if __name__ == '__main__':
    main()
