import streamlit as st
import pandas as pd
import datetime
from statsmodels.tsa.arima.model import ARIMA
import plotly.express as px
import pymongo
import os
from datetime import datetime, timedelta
import io
import altair as alt  
#from streamlit_extras.switch_page_button import switch_page
st.set_page_config(page_title="Revenue Forecasting", page_icon=":overview", layout="wide", initial_sidebar_state="collapsed")

def set_custom_styles():
    """
    Custom styles to hide Streamlit default elements and adjust margins.
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
    selected_page = selected_page or "Revenue_Analysis"
    # current_file = __file__.split("/")[-1]
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
    #   "/Yearly": "Yearly"
}
selected_page = url_to_page.get(url_path)
custom_top_bar(selected_page)
# -----------------------------------------------

# # Define a custom CSS style for the fixed header
# header_style = """
# position: fixed;
# top: 0;
# left: 0;
# width: 100%;
# # background-color: #1E90FF;
# color: white;
# padding: 10px;
# text-align: center;
# """

# # Create the fixed header using the custom CSS style
# st.markdown(f'<div style="{header_style}">Hotel Revenue Forecasting</div>', unsafe_allow_html=True)


connection_uri = "mongodb+srv://annu21312:6dPsrXPfhm19YxXl@hello.hes3iy5.mongodb.net/"
client = pymongo.MongoClient(connection_uri, serverSelectionTimeoutMS=30000)
database_name = "Revenue_Forecasting"
db = client[database_name]
collection = db["Revenue"]

# connection_uri = "mongodb://localhost:27017/
# client = pymongo.MongoClient(connection_uri)
# database_name = "revenue_database"
# db = client[database_name]
# collection = db["revenue_table1"]

# Retrieve the starting and ending "Business Date" values from the database
pipeline = [
    {"$group": {"_id": None, "minDate": {"$min": "$Business Date"}, "maxDate": {"$max": "$Business Date"}}}
]
result = list(collection.aggregate(pipeline))
if result:
    start_date_str = result[0]["minDate"]
    end_date_str = result[0]["maxDate"]
else:
    # Handle the case where there is no data in the collection
    start_date_str = datetime.now().strftime("%Y-%m-%d")
    end_date_str = datetime.now().strftime("%Y-%m-%d")

# Convert start_date_str and end_date_str to datetime objects
start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

st.markdown("\n")
st.markdown("\n")

col1, col2=st.columns((2))
with col1:
    date1 = st.date_input("Select Start Date:", start_date)
with col2:
    date2 = st.date_input("Select End Date:", end_date)
    
# Convert selected dates to ISO format for MongoDB query
date1 = date1.strftime("%Y-%m-%d")
date2 = date2.strftime("%Y-%m-%d")



query = {"Business Date": {"$gte": date1, "$lte": date2}}
# Fetch data from MongoDB
cursor = collection.find(query)
# Convert MongoDB cursor to DataFrame
df = pd.DataFrame(list(cursor))
chart_options = ["Revenue Breakdown", "Group Bookings", "Demand and Supply", "Customer Segmentation", "Ooo Rooms", "Inclusion Revenue", "Total Room Inventory"]
selected_option = chart_options[0]
selected_option = st.selectbox("Select Analysis", chart_options, format_func=lambda option: option)
df['Business Date'] = pd.to_datetime(df['Business Date'])
fig = None

if selected_option == "Revenue Breakdown":
    selected_columns = ["Room Revenue", "Individual Revenue", "Confirmed Group Revenue", "Tentative Group Revenue"]
    fig = px.bar(df, x="Business Date", y=selected_columns, barmode="stack", title="Revenue Breakdown")
elif selected_option == "Group Bookings":
    selected_columns = ["Confirmed Group Revenue", "Tentative Group Revenue"]
    fig = px.line(df, x="Business Date", y=selected_columns, title="Group Booking Trends")
elif selected_option == "Demand and Supply":
    selected_columns = ["Arrival Rooms", "Compliment Rooms"]
    fig = px.bar(df, x="Business Date", y=selected_columns, title="Supply and Demand")
elif selected_option == "Customer Segmentation":
    selected_columns = ["Individual Revenue", "Confirmed Group Revenue"]
    fig = px.line(df, x="Business Date", y=selected_columns, title="Customer Segmentation")
elif selected_option == "Ooo Rooms": #Out of Order (OOO) Rooms
    selected_columns = ["OOO Rooms"]
    fig = px.bar(df, x="Business Date", y=selected_columns, title="Out of Order (OOO) Rooms")
elif selected_option == "Inclusion Revenue":
    selected_columns = ["Inclusion Revenue"]
    fig = px.line(df, x="Business Date", y=selected_columns, title="Inclusion Revenue")
else:  # "Total Room Inventory"
    selected_columns = ["Total Room Inventory"]
    fig = px.bar(df, x="Business Date", y=selected_columns, title="Total Room Inventory")

# Customize the chart's appearance
fig.update_layout(
    xaxis_title="Business Date",
    yaxis_title="Value",
    template="plotly_dark",  # Apply a dark theme for aesthetics
    xaxis_rangeselector=dict(
        buttons=list([
            dict(count=7, label="1W", step="day"),
            dict(count=1, label="1M", step="month"),
            dict(count=3, label="3M", step="month"),
            dict(count=6, label="6M", step="month"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1Y", step="year"),
            dict(step="all")
            ]),
            x=0.01,  # Adjust the horizontal position of the rangeselector
            xanchor='left',  # Anchor the rangeselector to the left
        )
)

# Add interactivity with hover information
fig.update_traces(hoverinfo='y+name')

# Display the interactive chart
st.plotly_chart(fig)

# Provide an option to download the chart as an image
if st.button("Download Chart as Image"):
    st.image(fig.to_image(format="png"), use_container_width=True)
