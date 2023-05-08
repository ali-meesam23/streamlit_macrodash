from datetime import datetime
import pandas as pd
from polygon import RESTClient
import os

def smalL_chart(ticker='EURUSD', exch='FX'):
    ticker = ticker.upper()
    exch = exch.upper()
    return f"""
            <!-- TradingView Widget BEGIN -->
            <div class="tradingview-widget-container">
            <div class="tradingview-widget-container__widget"></div>
            <!-- <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/symbols/{ticker}/?exchange={exch}" rel="noopener" target="_blank"><span class="blue-text">EUR USD rates</span></a></div>  -->
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
            {{
            "symbol": "{exch}:{ticker}",
            "width": "290",
            "height": "250",
            "locale": "en",
            "dateRange": "3M",
            "colorTheme": "dark",
            "isTransparent": false,
            "autosize": false,
            "largeChartUrl": "",
            "chartOnly": false
            }}
            </script>
            </div>
            <!-- TradingView Widget END -->
            """


def get_candles(ticker='SPY', multiplier=1, timespan="day", from_="2022-01-01", to=""):
    client =RESTClient(os.getenv("POLYGON_API_KEY"))
    if to=="":
        to = datetime.now().strftime("%Y-%m-%d")
    bars = client.get_aggs(ticker=ticker, multiplier=1, timespan="day", from_=from_, to=to)
    candles = pd.DataFrame(bars).set_index('timestamp')
    candles.index = pd.to_datetime(candles.index, unit='ms').tz_localize('UTC').tz_convert('US/Eastern')
    candles = candles[['open', 'high', 'low', 'close', 'volume']]
    return candles