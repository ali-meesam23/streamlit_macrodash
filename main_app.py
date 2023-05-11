import streamlit as st
import os
import streamlit.components.v1 as components

from outlook import create_mini_chart_board, get_idx_news, macro_calendar
from helper import get_candles
from trending import *
from polygon import RESTClient
from datetime import datetime, timedelta
from USMacroData import MacroIndicators

client = RESTClient(st.secrets["POLYGON_API_KEY"])
macroindicators = MacroIndicators()


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
  selected_widget = st.sidebar.selectbox("Select Page", ["Outlook", "Sector Trends",'Ticker Trend','Yield Curve (comparison)','Yield Curve (history)'])
  if selected_widget == "Outlook":
      
      st.write("MacroEconomic Data:")
      COLS = list(macroindicators._latest_data[2].columns.tolist())
      rows= 3
      i = 0
      for _ in range(rows):
        _C = st.columns(len(COLS)//rows)
        for col in _C:  
          with col:
          # for c in COLS:
            val = str(round(macroindicators._latest_data[0][COLS[i]],2))
            change = str(round(macroindicators._latest_data[1][COLS[i]],2))
            st.metric(label=COLS[i], value=val, delta=change+"%")
          i+=1
          

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


  elif selected_widget == 'Yield Curve (history)':
  
    # Sidebar date selection  
    data = macroindicators.curves
    selected_date = st.sidebar.select_slider('Select a date', options=[d.strftime("%Y-%m-%d") for d in data.index],value=data.index[-1].strftime("%Y-%m-%d"))
    # # Display the plot
    fig = macroindicators.plot_yield_slider(selected_date)
    st.plotly_chart(fig)


  elif selected_widget == 'Yield Curve (comparison)':
    st.write("Monthly Yield % Change:")
    COLS = macroindicators.curves.columns.tolist()
    _C = st.columns(len(COLS))
    for i,col in enumerate(_C):
        with col:
        # for c in COLS:
          v = (macroindicators.curves).astype("str").iloc[-1]
          delta = round(macroindicators.curves.pct_change()*100,2).astype("str").iloc[-1]
          st.metric(label=COLS[i], value=v[COLS[i]]+"%", delta=delta[COLS[i]]+"%")

    st.plotly_chart(macroindicators.plot_yield_curve)


if __name__ == "__main__":
    main()
