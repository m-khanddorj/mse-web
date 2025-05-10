import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from io import StringIO

# Import utility modules
from utils.data_loader import load_csv_data, validate_csv_data
from utils.technical_analysis import (
    calculate_moving_average,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
)
from utils.visualization import (
    create_price_chart,
    create_volume_chart,
    create_indicator_chart,
)

# Set page configuration
st.set_page_config(page_title="Хувьцааны Үнийн Шинжилгээ", page_icon="📈", layout="wide")

# App title and description
st.title("📈 Хувьцааны Үнийн Шинжилгээ")
st.markdown(
    """
Энэхүү програм нь хувьцааны үнийн өгөгдлийг дүрслэх, шинжлэх боломжийг олгоно.
Өөрийн өгөгдлийг оруулах эсвэл жишээ өгөгдлийг ашиглана уу.
"""
)

# Sidebar for inputs
st.sidebar.header("Тохиргоо")

# Option to use sample data or upload custom data
data_option = st.sidebar.radio(
    "Өгөгдлийн эх үүсвэрийг сонгоно уу:",
    ("Хувьцаа сонгох", "Өөрийн CSV файлыг оруулах"),
)

data = None

if data_option == "Хувьцаа сонгох":
    # List sample files
    sample_files = sorted([f for f in os.listdir("sample_data") if f.endswith(".csv")])
    if sample_files:
        selected_sample = st.selectbox(
            "Жишээ хувьцааг сонгоно уу:", sample_files,
            format_func = lambda x: x.split(".")[0],
        )
        data = load_csv_data(f"sample_data/{selected_sample}")
        st.info(f"Жишээ өгөгдөл ачааллаа: {selected_sample}")
    else:
        st.warning("Жишээ файл олдсонгүй.")
else:
    # File uploader
    uploaded_file = st.file_uploader("CSV файл оруулна уу", type=["csv"])

    if uploaded_file is not None:
        # Read the file as string
        string_data = StringIO(uploaded_file.getvalue().decode("utf-8"))

        # Validate and load the data
        is_valid, message = validate_csv_data(string_data)
        if is_valid:
            string_data.seek(0)  # Reset file pointer
            data = pd.read_csv(string_data)
            # Convert date column to datetime
            if "Date" in data.columns:
                data["Date"] = pd.to_datetime(data["Date"])
            elif "date" in data.columns:
                data["Date"] = pd.to_datetime(data["date"])
                data = data.drop("date", axis=1)

            st.success("Өгөгдөл амжилттай ачааллаа!")
        else:
            st.error(f"Өгөгдлийн формат буруу байна: {message}")

# If data is loaded successfully
if data is not None:
    # Display data summary
    st.subheader("Өгөгдлийн Тойм")
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Нийт бичлэгүүд:** {len(data)}")
        if "Date" in data.columns:
            st.write(
                f"**Огнооны хүрээ:** {data['Date'].min().date()} - {data['Date'].max().date()}"
            )

    with col2:
        if all(col in data.columns for col in ["Open", "High", "Low", "Close"]):
            latest_data = data.iloc[-1]
            st.write(f"**Хамгийн сүүлийн үнэ (Хаалт):** ${latest_data['Close']:.2f}")
            st.write(
                f"**Latest trading range:** ${latest_data['Low']:.2f} - ${latest_data['High']:.2f}"
            )

    # Date range selection

    st.subheader("Date Range")
    col1,col2 = st.columns(2)
    # Calculate default dates (last 6 months if data allows)
    if "Date" in data.columns:
        end_date = data["Date"].max()
        start_date = max(data["Date"].min(), end_date - timedelta(days=180))

        # Date range selector
        selected_start_date = col1.date_input(
            "Start date",
            value=start_date,
            min_value=data["Date"].min(),
            max_value=data["Date"].max(),
        )

        selected_end_date = col2.date_input(
            "End date",
            value=end_date,
            min_value=data["Date"].min(),
            max_value=data["Date"].max(),
        )

        # Filter data based on selected date range
        filtered_data = data[
            (data["Date"] >= pd.Timestamp(selected_start_date))
            & (data["Date"] <= pd.Timestamp(selected_end_date))
        ]
    else:
        filtered_data = data
        st.warning("No date column found. Showing all data.")

    # Chart type selection
    # chart_type = st.sidebar.selectbox("Chart Type", ("Line", "Candlestick"))
    chart_type = "Line"

    # Technical Indicators selection
    st.sidebar.subheader("Technical Indicators")
    show_ma = st.sidebar.checkbox("Moving Averages", value=True)

    if show_ma:
        ma_periods = st.sidebar.multiselect(
            "MA Periods", options=[5, 10, 20, 50, 100, 200], default=[]
        )

    show_rsi = st.sidebar.checkbox("RSI (Relative Strength Index)", value=True)
    if show_rsi:
        rsi_period = st.sidebar.slider(
            "RSI Period", min_value=7, max_value=21, value=14
        )

    show_macd = st.sidebar.checkbox(
        "MACD (Moving Average Convergence Divergence)", value=False
    )
    if show_macd:
        macd_fast = st.sidebar.slider(
            "MACD Fast Period", min_value=8, max_value=20, value=12
        )
        macd_slow = st.sidebar.slider(
            "MACD Slow Period", min_value=21, max_value=30, value=26
        )
        macd_signal = st.sidebar.slider(
            "MACD Signal Period", min_value=5, max_value=12, value=9
        )

    show_bbands = st.sidebar.checkbox("Bollinger Bands", value=True)
    if show_bbands:
        bbands_period = st.sidebar.slider(
            "Bollinger Bands Period", min_value=5, max_value=50, value=20
        )
        bbands_std = st.sidebar.slider(
            "Standard Deviation", min_value=1, max_value=4, value=2
        )

    # Calculate technical indicators if requested
    if "Close" in filtered_data.columns:
        # Calculate Moving Averages
        if show_ma and ma_periods:
            for period in ma_periods:
                filtered_data[f"MA_{period}"] = calculate_moving_average(
                    filtered_data["Close"], period
                )

        # Calculate RSI
        if show_rsi:
            filtered_data["RSI"] = calculate_rsi(filtered_data["Close"], rsi_period)

        # Calculate MACD
        if show_macd:
            (
                filtered_data["MACD"],
                filtered_data["MACD_Signal"],
                filtered_data["MACD_Histogram"],
            ) = calculate_macd(
                filtered_data["Close"],
                fast_period=macd_fast,
                slow_period=macd_slow,
                signal_period=macd_signal,
            )

        # Calculate Bollinger Bands
        if show_bbands:
            (
                filtered_data["BB_Upper"],
                filtered_data["BB_Middle"],
                filtered_data["BB_Lower"],
            ) = calculate_bollinger_bands(
                filtered_data["Close"], window=bbands_period, num_std=bbands_std
            )

    # Create and display charts
    st.subheader("Price Chart")

    # Main price chart
    # Note: Bollinger Bands are automatically displayed if they've been calculated
    fig_price = create_price_chart(
        selected_sample.split(".")[0],
        filtered_data,
        chart_type=chart_type,
        ma_periods=ma_periods if show_ma else [],
    )
    st.plotly_chart(fig_price, use_container_width=True)

    # Display technical indicators in separate charts
    if show_rsi:
        st.subheader("RSI (Relative Strength Index)")
        fig_rsi = create_indicator_chart(
            filtered_data, "RSI", y_min=0, y_max=100, reference_levels=[30, 70]
        )
        st.plotly_chart(fig_rsi, use_container_width=True)

    if show_macd:
        st.subheader("MACD (Moving Average Convergence Divergence)")
        fig_macd = create_indicator_chart(
            filtered_data,
            main_line="MACD",
            secondary_line="MACD_Signal",
            histogram="MACD_Histogram",
        )
        st.plotly_chart(fig_macd, use_container_width=True)

    # Volume chart
    if "Volume" in filtered_data.columns:
        st.subheader("Volume")
        fig_volume = create_volume_chart(filtered_data)
        st.plotly_chart(fig_volume, use_container_width=True)

    # Display statistics
    st.subheader("Statistics")

    # Select necessary columns for statistics
    stat_cols = [
        col
        for col in ["Open", "High", "Low", "Close", "Volume"]
        if col in filtered_data.columns
    ]

    if stat_cols:
        stats_df = filtered_data[stat_cols].describe()

        # Round to 2 decimal places for better display
        stats_df = stats_df.round(2)

        # Display statistics
        st.dataframe(stats_df)

    # Show raw data
    if st.checkbox("Show raw data"):
        st.subheader("Raw Data")
        st.dataframe(filtered_data)

else:
    # Display instructions when no data is loaded
    st.info(
        "Please upload a CSV file with stock price data or select a sample file to begin."
    )

    st.markdown(
        """
    ### Expected CSV Format
    
    Your CSV file should have the following columns:
    - Date (in YYYY-MM-DD format)
    - Open (opening price)
    - High (highest price)
    - Low (lowest price)
    - Close (closing price)
    - Volume (optional)
    
    Example:
    ```
    Date,Open,High,Low,Close,Volume
    2021-01-04,133.52,133.61,126.76,129.41,143301900
    2021-01-05,128.89,131.74,128.43,131.01,97664900
    ...
    ```
    """
    )
