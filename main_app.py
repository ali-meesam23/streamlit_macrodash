import streamlit as st
import os
import streamlit.components.v1 as components

from outlook import create_mini_chart_board, get_idx_news
from helper import get_candles
from trending import *
from polygon import RESTClient

client = RESTClient(os.getenv("POLYGON_API_KEY"))



def main():
    # Add sidebar
    st.sidebar.title("Sidebar")
    selected_widget = st.sidebar.selectbox("Select Page", ["Outlook", "Sector Trends", "Widget 3"])
    if selected_widget == "Outlook":
        # Custom CSS for responsiveness
        st.markdown(
            """
            <style>
            @media only screen and (max-width: 600px) {
                .tradingview-widget-container {
                    height: 400px !important;
                }
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    
        create_mini_chart_board()
        st.write(" ")
        get_idx_news()
    elif selected_widget == 'Sector Trends':
        data_dict = {}
        tickers = ['SPY','QQQ','XLE','XLF','XLK']
        for ticker in tickers:
            data_dict[ticker] = get_candles(ticker)
        stats_dict = {}
        for ticker in data_dict:
            # GET EXTREMA
            ext_df = find_extremas(data_dict[ticker])
            # GET STATS
            stats_dict[ticker] = get_stats(ext_df)
            # PLOT
            print(plot(ext_df,ticker).show())

if __name__ == "__main__":
    main()
