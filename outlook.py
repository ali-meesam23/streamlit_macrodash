import streamlit.components.v1 as components
import streamlit as st
from helper import smalL_chart

def create_mini_chart_board():
    col_height = 260
    col_width = 900//3
    st.title("MacroEconomic Outlook")
    
    # st.write("Overview Page")
    
    # Create a 3 column, 2 row layout
    col1, _1, col2, _2, col3 = st.columns(5)
    with col1:
        components.html(
            smalL_chart('DXY','CAPITALCOM'), height=col_height, width=col_width
        )

    with _1:
        st.write(" ")

    with col2:
        components.html(
            smalL_chart('OIL_CRUDE','CAPITALCOM'), height=col_height, width=col_width
        )
    with _2:
        st.write(" ")

    with col3:
        components.html(
            smalL_chart('ES1!','CME_MINI'), height=col_height, width=col_width
        )

    col1, _1, col2, _2, col3 = st.columns(5)
    with col1:
        components.html(
            smalL_chart('10Y1!','CBOT_MINI'), height=col_height, width=col_width
        )

    with _1:
        pass

    with col2:
        components.html(
            smalL_chart('TOTAL','CRYPTOCAP'), height=col_height, width=col_width
        )
    with _2:
        pass
    
    with col3:
        components.html(
            smalL_chart('VIX','CAPITALCOM'), height=col_height, width=col_width
        )

def get_idx_news():
    news = """<!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container" style="display: flex; justify-content: center; align-items: center; height: 600px;">
    <div class="tradingview-widget-container__widget"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-timeline.js" async>
    {
    "feedMode": "market",
    "market": "index",
    "colorTheme": "dark",
    "isTransparent": false,
    "displayMode": "regular",
    "width": "870",
    "height": "400",
    "locale": "en"
    }
    </script>
    </div>
    <!-- TradingView Widget END -->"""

    components.html(
            news, height=800, width=900
    )

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