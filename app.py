#aaaaaaaaaaaaaaaaa
#arun
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import pymongo
from datetime import datetime
import os

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
    selected_page = selected_page or "Home"
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
            <a style="color: {'red' if selected_page == 'Market' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'market' else 'none'}" href="/market" target="_self">market</a>
            <a style="color: {'red' if selected_page == 'Prediction' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'Prediction' else 'none'}" href="/Prediction" target="_self">Prediction</a>
            <a style="color: {'red' if selected_page == 'trend' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'trend' else 'none'}" href="/trend" target="_self">trend</a>
            </div>
    """
    st.markdown(custom_top_bar, unsafe_allow_html=True)

def new_tab_content():
    st.title("NewTab Content")
    st.write("Content for the new tab goes here.")


# custom_top_bar()
set_custom_styles()

url_path = st.experimental_get_query_params().get("pages", [""])[0]
url_to_page = {
    "/Home": "Home",
    "/Daily_Overview": "Daily_Overview",
    "/Revenue_Analysis": "Revenue_Analysis",
    "/Report": "Report",
    "/upload": "Upload",
    "/market": "market",
    "/Prediction": "Prediction",
    "/trend": "trend",


    
}
selected_page = url_to_page.get(url_path)
custom_top_bar(selected_page)
# -----------------------------------------------
def m():
    
    # Define the layout using HTML and CSS
    st.markdown(
        """
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                margin: 0;
            }
            .container {
                max-width: 800px;
                margin: auto;
                padding: 20px;
            }
            .header {
                text-align: left;
                padding: 20px;
                color: #333; /* Dark text color */
                # border-radius: 10px;
            }
            .sub-header {
                text-align: left;
                padding: 10px;
                color: #555; /* Slightly darker text color */
            }
            .image-container {
                text-align: center;
                padding: 20px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Page header
    # st.markdown("<div class='header'><h1>Hotel Revenue Forecasting</h1></div>", unsafe_allow_html=True)
    col1,col2=st.columns(2)
    with col1:
        st.markdown("<div class='sub-header'><h3>Accurate forecasts for your hotel!!</h3></div>", unsafe_allow_html=True)
        st.write("Welcome to the Hotel Revenue Forecasting website. Use the tools and features provided to analyze and predict the revenue for your hotel business.")
    with col2:
        st.image("imagerf.png")   
    st.markdown("</div>", unsafe_allow_html=True)
    # st.markdown("</div>", unsafe_allow_html=True)

# if __name__ == "__main__":
m()

# MongoDB connection setup
connection_uri = "mongodb+srv://annu21312:6dPsrXPfhm19YxXl@hello.hes3iy5.mongodb.net/"
client = pymongo.MongoClient(connection_uri, serverSelectionTimeoutMS=30000)
database_name = "Revenue_Forecasting"
db = client[database_name]
collection = db["Summary"]
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
@st.cache
def get_data(start_date, end_date):
    query = {"Business Date": {"$gte": start_date, "$lte": end_date}}
    cursor = collection.find(query)
    return pd.DataFrame(list(cursor))


col1, col2=st.columns((2))
with col1:
    date1 = st.date_input("Select Start Date:", start_date)
with col2:
    date2 = st.date_input("Select End Date:", end_date)
date1 = date1.strftime("%Y-%m-%d")
date2 = date2.strftime("%Y-%m-%d")
query = {"Business Date": {"$gte": date1, "$lte": date2}}

#---------------------------------------------------------------------------
cursor = collection.find(query)
df = pd.DataFrame(list(cursor))
if not df.empty:
    # Display 'Room Revenue' for the selected date range
    total_room_revenue = df['Room Revenue'].sum()
    col1, col2 = st.columns((1, 1))
    # st.markdown("<div class='section-title'>Room Revenue Over Time</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-weight: bold; font-size: 20px;'>Room Revenue Over Time</div>", unsafe_allow_html=True)

    fig = px.line(df, x='Business Date', y='Room Revenue',
      labels={'Business Date': 'Date', 'Room Revenue': 'Revenue'},
      line_shape='linear',
      color_discrete_sequence=['#0074D9']
    #   color_discrete_sequence=['#1f77b4']
      )  

    fig.update_layout(
    xaxis_title_text='Date',
    yaxis_title_text='Revenue',
    xaxis_title_font_size=16,  # Increase the x-axis label font size
    yaxis_title_font_size=16,  # Increase the y-axis label font size
    xaxis_rangeslider_visible=True,
    xaxis_rangeslider_thickness=0.03,  # Adjust the thickness of the range slider
    xaxis_rangeslider_bgcolor='lightgray',  # Set the background color of the range slider
    xaxis_rangeslider_bordercolor='gray',  # Set the border color of the range slider
    xaxis_rangeslider_borderwidth=1,  # Set the border width of the range slider
    xaxis_rangeslider_range=[date1, date2],  # Set the initial date range
    xaxis_range=[date1, date2],
    xaxis_rangeselector=dict(
        buttons=list([
            dict(count=7, label="1W", step="day", stepmode="backward"),
            dict(count=1, label="1M", step="month", stepmode="backward"),
            dict(count=3, label="3M", step="month", stepmode="backward"),
            dict(count=6, label="6M", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1Y", step="year", stepmode="backward"),
            dict(step="all")
            ]),
            x=0.01,  # Adjust the horizontal position of the rangeselector
            xanchor='left',  # Anchor the rangeselector to the left
        )
    )
    # fig.update_traces(mode="lines+markers", hovertemplate="Date: %{x}<br>Revenue: $%{y:,.2f}<extra></extra>")
    fig.update_traces(mode="lines+markers", line=dict(width=2), marker=dict(size=6))
    fig.update_xaxes(type='date', showgrid=True, gridwidth=0.5, gridcolor='lightgray')  # Add gridlines
    fig.update_yaxes(title_text='Revenue', showgrid=True, gridwidth=0.5, gridcolor='lightgray')  # Add gridlines
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))

    # Customize the layout
    fig.update_layout(
        legend_title='Legend',
        font=dict(family='Arial', size=14),
        # xaxis=dict(linecolor='black', linewidth=1),  # Set x-axis border line color and width
        # yaxis=dict(linecolor='black', linewidth=1),  # Set y-axis border line color and width
        shapes=[
            dict(
                type='line',
                x0=0,
                x1=1,
                y0=0,
                y1=0,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
            dict(
                type='line',
                x0=0,
                x1=0,
                y0=0,
                y1=1,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
            dict(
                type='line',
                x0=1,
                x1=1,
                y0=0,
                y1=1,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
            dict(
                type='line',
                x0=0,
                x1=1,
                y0=1,
                y1=1,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
        ],
    )
   
    st.plotly_chart(fig)
    st.write(f"Total Room Revenue for the selected date range: ${total_room_revenue:.2f}")

    # # Button to show/hide the DataFrame
    # if 'show_df' not in st.session_state:
    #     st.session_state.show_df = False

    # if st.button("Show Filtered Data"):
    #     st.session_state.show_df = not st.session_state.show_df

    # if st.session_state.show_df:
    #     st.write(df)
    show_df = st.checkbox("Show Filtered Data", value=False)
    if show_df:
        st.write(df)

else:
    st.warning("No data available for the selected date range.")
