import streamlit as st
import pandas as pd
import datetime
import pymongo
import os
from datetime import datetime, timedelta
from datetime import datetime, timedelta
#from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Daily Overview", page_icon=":overview", layout="wide", initial_sidebar_state="collapsed")
# st.set_page_config(page_title="Revenue Forecasting", page_icon=":overview", layout="wide", initial_sidebar_state="collapsed")
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
    selected_page = selected_page or "Daily_Overview"
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
            <a style="color: {'red' if selected_page == 'trend' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'trend' else 'none'}" href="/trend" target="_self">trend</a>
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
  #  "/Prediction": "Prediction",
    "/upload": "Upload",
    "/market": "market",
      "/Prediction": "Prediction",
      "/trend": "trend",
}
selected_page = url_to_page.get(url_path)
custom_top_bar(selected_page)
# --------------------------------------------------
# MongoDB connection setup
connection_uri = "mongodb+srv://annu21312:6dPsrXPfhm19YxXl@hello.hes3iy5.mongodb.net/"
client = pymongo.MongoClient(connection_uri, serverSelectionTimeoutMS=30000)
database_name = "Revenue_Forecasting"
db = client[database_name]
collection = db["Summary"]

last_business_date_result = collection.find({}, {"Business Date": 1}).sort("Business Date", pymongo.DESCENDING).limit(1)
last_business_date = last_business_date_result[0]["Business Date"] if collection.count_documents({}) > 0 else datetime.now().strftime("%Y-%m-%d")

# current_date = datetime.now().strftime("%Y-%m-%d")
previous_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# Dropdown options for the second date
date_options = ["Previous Date", "Last Year Same Date", "Last Year Same Weekday"]
# st.markdown("\n\n")
# st.markdown("\n\n")
# st.markdown("\n\n")

st.markdown("<div class='section-title'>Daily Overview</div>", unsafe_allow_html=True)

date1_default = last_business_date
# date1_default = current_date
date2_default = previous_date
col1, col2 = st.columns(2)
with col1:
    date1 = st.date_input("Select Date:", datetime.strptime(date1_default, "%Y-%m-%d"), key="date_input_id")
    st.markdown(
    f"""
    <style>
        #{date1} {{
            position: absolute;
            bottom: 0;
        }}
    </style>
    """,
    unsafe_allow_html=True
)
with col2:
    date_option = st.selectbox("Relative to:", date_options)

    if date_option == "Previous Date":
        date2 = (date1 - timedelta(days=1)).strftime("%Y-%m-%d")
    elif date_option == "Last Year Same Date":
        date2 = (date1 - timedelta(days=365)).strftime("%Y-%m-%d")
    elif date_option == "Last Year Same Weekday":
        date2 = (date1 - timedelta(weeks=52)).strftime("%Y-%m-%d")

# with col2:
    date2 =  datetime.strptime(date2, "%Y-%m-%d")
# Convert selected dates to ISO format for MongoDB query
date1 = date1.strftime("%Y-%m-%d")
date2 = date2.strftime("%Y-%m-%d")

css = """
    body {
        background-color: #f8f9fa !important;
    }

    .container {
        margin: 20px;
    }

    .header {
        background-color: #1E90FF;
        color: white;
        padding: 10px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }

    .date-display {
        font-size: 18px;
        margin-bottom: 20px;
    }

    .card {
        flex-basis: 30%;
        padding: 20px;
        margin: 10px 0;
        border-radius: 10px;
        box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }

    .card:hover {
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
    }

    .card-values {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .card-values div {
        text-align: center;
        flex-basis: 33%;
    }

    .card-values div.left {
        text-align: left;
    }

    .card-values div.right {
        text-align: right;
    }
"""
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
st.markdown(f"<div class='date-display'> {date1} vs {date2} incl. tentative</div>", unsafe_allow_html=True)


def display_data():
    css = """
    body {
        background-color: #ffffff;
        color: #000000;
    }
    .card-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
    }

    .card {
        flex-basis: 30%; /* Set card width to 30% for three cards in a row */
        # background-color: #fff;
        padding: 20px;
        margin: 10px 0;
        border-radius: 10px;
        box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.1);
        # transition: transform 0.2s, box-shadow 0.2s;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;

        color: {card_text_color};
    }
    .card:hover {
        # transform: scale(1.02); /* Add zoom effect on hover */
        # transform: scale(1.03);
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
    }

    .section-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
        color: {card_text_color};
    }
    """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    # MongoDB query to find data for the two selected dates
    query = {"Business Date": {"$in": [date1, date2]}}
    cursor = collection.find(query)
    df = pd.DataFrame(list(cursor))
    
    if not df.empty:
        date1_data = df[df["Business Date"] == date1]
        date2_data = df[df["Business Date"] == date2]
        # Check if data exists for both selected dates
        if not date1_data.empty and not date2_data.empty:
            def display_field(field_name, date1_data, date2_data):
                field_diff = date2_data[field_name].iloc[0] - date1_data[field_name].iloc[0]
                color = "red" if isinstance(field_diff, (int, float)) and field_diff < 0 else "green"
                st.markdown(
                    f"<div class='card'>"
                    f"<p>{field_name}</p>"

                    f"<div class='card-values'>"
                    f"<div class='card-values' style='display: flex; justify-content: space-between; align-items: center;'>"
                    f"<div style='text-align: left; flex-basis: 33%; color: {color};'>{date1_data[field_name].iloc[0]}</div>"
                    f"<div style='text-align: center; flex-basis: 33%; font-weight: bold;'>{field_diff:.2f}</div>"
                    f"<div style='text-align: right; flex-basis: 33%;'>{date2_data[field_name].iloc[0]}</div>"
                    f"</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            # Display values for each field
            fields = ["Occupancy","Room Revenue", "Arrival Rooms", "OOO Rooms", "Pax", "Rooms Sold", "Dep Rooms", "House Use"]
            col1, col2, col3 = st.columns(3)
            for i, field in enumerate(fields):
                if i % 3 == 0:
                    card_column = col1
                elif i % 3 == 1:
                    card_column = col2
                else:
                    card_column = col3
                with card_column:
                    display_field(field, date1_data, date2_data)

        else:
            st.warning("Data not available for one or both of the selected dates.")

display_data()