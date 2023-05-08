import streamlit as st
import os
import streamlit.components.v1 as components

from outlook import create_mini_chart_board, get_idx_news, macro_calendar
from helper import get_candles
from trending import *
from polygon import RESTClient
from datetime import datetime, timedelta

client = RESTClient(st.secrets["POLYGON_API_KEY"])

tape_widget = """<!-- TradingView Widget BEGIN -->
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget"></div>
  <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/markets/" rel="noopener" target="_blank"><span class="blue-text">Markets today</span></a> by TradingView</div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-tickers.js" async>
  {
  "symbols": [
    {
      "proName": "FOREXCOM:SPXUSD",
      "title": "S&P 500"
    },
    {
      "proName": "FOREXCOM:NSXUSD",
      "title": "US 100"
    },
    {
      "proName": "FX_IDC:EURUSD",
      "title": "EUR/USD"
    },
    {
      "proName": "BITSTAMP:BTCUSD",
      "title": "Bitcoin"
    },
    {
      "proName": "BITSTAMP:ETHUSD",
      "title": "Ethereum"
    }
  ],
  "colorTheme": "dark",
  "isTransparent": false,
  "showSymbolLogo": true,
  "locale": "en"
}
  </script>
</div>
<!-- TradingView Widget END -->"""
components.html(tape_widget, width=900)

def main():
    # Add sidebar
    st.sidebar.title("Sidebar")
    selected_widget = st.sidebar.selectbox("Select Page", ["Outlook", "Sector Trends",'Ticker Trend'])
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
        st.write(" ")
        macro_calendar()

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
            st.plotly_chart(plot(ext_df,ticker))
            
    elif selected_widget == 'Ticker Trend':
        ticker = st.sidebar.text_input("Ticker")
        if ticker:
            ticker = ticker.upper()
            # GET EXTREMA
            ext_df = find_extremas(get_candles(ticker))
            # GET STATS
            stats = get_stats(ext_df)
            # PLOT
            st.plotly_chart(plot(ext_df,ticker))
        else:
            st.write("Enter a ticker in the sidebar to review the chart....")

if __name__ == "__main__":
    main()
