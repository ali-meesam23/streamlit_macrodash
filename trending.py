# GET DATA
import datetime
import pandas as pd
import polygon as pg
import os
import numpy as np
from scipy.signal import argrelextrema
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.io as pio

# GENERATE FULL DATAFRAME WITH SIGNALS

def find_extremas(df,ORDER=7, COL='close'):

    _price_smoothed = df[COL].rolling(window=ORDER).mean()
    _price_smoothed.fillna(df[COL],inplace=True)
    df['price'] = _price_smoothed
    ilocs_min = argrelextrema(_price_smoothed.values, np.less_equal, order=ORDER, mode='wrap')[0]
    ilocs_max = argrelextrema(_price_smoothed.values, np.greater_equal, order=ORDER,mode='wrap')[0]

    m = [0] * len(_price_smoothed)
    minmax = np.array(m)
    minmax[ilocs_min] = -1
    minmax[ilocs_max] = 1
    df['minMax'] = minmax
    df[['CandleCount','perc','pts']] = [0,0,0]

    pivots = df[df.minMax!=0].index
    if len(pivots)>0:
        for i in range(1,len(pivots)):
            start = pivots[i-1]
            end = pivots[i]
            _df = df[(df.index>=start) & (df.index<end)]
            # Starting candlecount at 0 being the first candle
            df.loc[start,'CandleCount'] = len(_df)-1
            df.loc[start,'perc'] = (df[COL].loc[end] / df[COL].loc[start] -1)*100
            df.loc[start, 'pts'] = df[COL].loc[end] - df[COL].loc[start]

        # LAST EXTREMA
        # Starting candlecount at 0 being the first candle
        df.loc[end,'CandleCount'] = len(df[df.index>=end])-1
        df.loc[end,'perc'] = (df[COL].iloc[-1] / df[COL].loc[end] -1) *100
        df.loc[end, 'pts'] = df[COL].iloc[-1] - df[COL].loc[end]
    else:
        df['CandleCount'] = 0
        df['perc'] = 0
        df['pts'] = 0

    return df

# GENERATE STATS

def get_stats(extrema_df):
    ups = extrema_df[extrema_df.minMax==-1][['CandleCount','perc','pts']].mean()
    downs = extrema_df[extrema_df.minMax==1][['CandleCount','perc','pts']].mean()
    box = f"""UPSIDE:\nBasis PTS: {int(ups.pts*100)} cents\n% Swing: {round(ups.perc,2)}%\nCandles: {int(ups.CandleCount)} \n\nDOWNSIDE:\nBasis PTS: {int(downs.pts*100)} cents\n% Swing: {round(downs.perc,2)}%\nCandles: {int(downs.CandleCount)}"""
    print(box)
    LAST = extrema_df[extrema_df.minMax!=0].iloc[-1]
    signal = 'Down' if LAST.minMax==1 else "UP"
    _ = "- $" if signal=='Down' else "+ $"
    pts = _+ f'{abs(LAST.pts):,.2f}'
    perc = f'{LAST.perc:.2f}%'
    last_signal = f"{LAST.name.strftime('%Y-%m-%d')} ({signal})" + '\n' + f"Since: ( {pts} ) ( {perc} )"
    stats = {
        'ups':ups,
        'downs':downs,
        'last': last_signal,
        'box': box
    }
    return stats


def plot(df,ticker,day_range=None):
    stats = get_stats(df)
    max_df = df[df.minMax!=1]
    min_df = df[df.minMax!=-1]

    slider = False
    if not day_range:
        _df = df
    else:
        if ":" in day_range:
            l,u = day_range.split(":")
            _df = df.loc[l:u]
            _max_df = max_df.loc[l:u]
            _min_df = min_df.loc[l:u]
        else:
            slider=False
            _df =df.loc[day_range]
            _max_df = max_df[day_range]
            _min_df = min_df[day_range]

    fig = make_subplots(rows=2,cols=1, shared_xaxes=True,
                    vertical_spacing=0.07, subplot_titles=[ticker+" - "+get_trend(df)],
                    row_width=[0.15,0.85],
                    specs=[
                        [{"secondary_y": True}],
                        [{"type": "bar"}]
                    ])

    # fig.layout.title=f'{ticker}'

    # Plot OHLC on 1st row
    fig.add_trace(go.Candlestick(x=_df.index,open=_df.open,high=_df.high, low=_df.low, close=_df.close, name=time_frame),
                row=1,col=1)


    fig.add_annotation(
        x=1.15,
        y=0.3,
        xref='paper',
        yref='paper',
        text=stats['box'].replace("\n",'<br>'),
        font=dict(size=12),
        showarrow=False,
        align='right',
        bgcolor='rgba(255, 255, 255, 0.2)'
    )

    fig.add_annotation(
        x=1,
        y=1.1,
        xref='paper',
        yref='paper',
        text=stats['last'].replace("\n",'<br>'),
        font=dict(size=12),
        showarrow=False,
        align='right',
    )
    

    fig.add_trace(
        go.Scatter(
            x=_df[_df.minMax==1].index,           # x-coordinates of trace
            y=_df[_df.minMax==1].high,          # y-coordinates of trace
            name='Max',
            mode='markers',   # scatter mode (more in UG section 1)
            # text = label1, 
            textposition='top center',
            marker = dict(size = 15, color = 'purple', symbol = 'triangle-down'), # Add symbol here!
        )
    )

    fig.add_trace(
        go.Scatter(
            x=_df[_df.minMax==-1].index,           # x-coordinates of trace
            y=_df[_df.minMax==-1].low,          # y-coordinates of trace
            name='Min',
            mode='markers',   # scatter mode (more in UG section 1)
            # text = label1, 
            textposition='top center',
            marker = dict(size = 15, color = 'Green', symbol = 'triangle-up'), # Add symbol here!
        )
    )


    # Bar trade for Volume on 2nd row without legend
    fig.add_trace(go.Bar(x=_df.index,y=_df.volume,name='Volume',showlegend=True),
                    row=2,col=1)

    fig.add_trace(go.Scatter(x=_df.index,y=_df.volume.rolling(5).mean(),name='Vol5'),
                                row=2,col=1)

    fig.update_layout(
                    height=720
                )


    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.update_yaxes(autorange=True,automargin=True)
    # fig.update_xaxes(type='category')
    fig.update_xaxes(
        dtick="M1",
        tickformat="%b\n%Y",
        ticklabelmode="period")
    # fig.show()
    return fig



def get_trend(df):
    # GENERATE TREND
    # def signal(self):        
    Trend_Strength = {
    -3 : 'Strong Down Trend',
    -2 : "Down Trend",
    -1 : "Weak Down Trend",
    0 : 'No Trend',
    1 : "Weak Up Trend",
    2 : 'Up Trend',
    3 : "Strong Up Trend"
    }

    current_trend = 0
    __df = df[df.minMax!=0]

    if len(__df)>=8:
        for i in range(3):
            i+=1
            if i==1:
                _df = __df.iloc[-4:]
            else:
                _df = __df.iloc[-4-i:-i]

            # Get latest trend
            x1 = _df.iloc[0].close
            x2 = _df.iloc[1].close
            x3 = _df.iloc[2].close
            x4 = _df.iloc[3].close

            # print(f"Date: {_df.iloc[-1].name}: ",end=' ')

            # UPTREND LOGIC
            if x1<x2 and x3<x4 and x3>x1 and x4>x2:
                trend = -3
                # print("Strong Downtrend",end=" ")
            elif (x1<x2 and x3<x4) and not (x3 > x1 and x4 > x2):
                trend = -2
                # print("Downtrend",end=" ")
            elif (x4>x2) and not (x3>x1):
                trend = -1
                # print("Weak Downtrend",end=" ")
            elif x1>x2 and x3>x4 and x3<x1 and x4<x2:
                trend = 3
                # print("Strong Up Trend",end=" ")
            elif (x1>x2 and x3>x4) and not (x3<x1 and x4<x2):
                trend = 2
                # print("Uptrend",end=" ")
            elif (x4<x2) and not (x3<x1):
                trend = 1
                # print("Weak Uptrend",end=" ")
            else:
                # print('Not Trending',end=" ")
                trend = 0
            # print(f"${_df.iloc[-1].Close}")
            # print("*"*5)
            if i==1:
                current_trend = trend
        # print(f'Current Price: ${df.iloc[-1].Close}')
    return Trend_Strength[current_trend]    