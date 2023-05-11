import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import plotly.express as px

@st.cache_resource
class MacroIndicators:
    def __init__(self):
        self.KEY = os.getenv('ALPHA_PRO')

        self.curves = self.yield_curve(interval='monthly')
    
    def real_gdp(self,interval='quarterly'):
        """
        interval: quarterly | annual
        """
        interval = 'quarterly'
        url = f'https://www.alphavantage.co/query?function=REAL_GDP&interval={interval}&datatype=csv&apikey={self.KEY}'
        try:
            print("Requesting: RealGDP")
            df = pd.read_csv(url,index_col=0,parse_dates=True)
            df.sort_index(inplace=True)
            return df
        except Exception as e:
            print(e)
            return pd.DataFrame()
    
    def treasury_yeild(self,interval='daily',maturity='10year',datatype='csv'):
        """
        interval: daily, weekly, monthly
        maturity: 3month, 2year, 5year, 7year, 10year, 30year
        datatype: csv json
        """
        url = f'https://www.alphavantage.co/query?function=TREASURY_YIELD&interval={interval}&maturity={maturity}&datatype={datatype}&apikey={self.KEY}'
        try:
            print(f"Requesting: {maturity} Yield")
            df = pd.read_csv(url,index_col=0,parse_dates=True)
            df.sort_index(inplace=True)
            df.value = df.value.apply(lambda x: float(x) if x!="." else 0)
            return df
        except Exception as e:
            print(e)
            return pd.DataFrame()
    

    def yield_curve(self, interval='monthly'):

        maturities = '3month, 2year, 5year, 7year, 10year, 30year'.split(', ')

        df = pd.DataFrame()
        for maturity in maturities:
            df[maturity] = self.treasury_yeild(interval=interval,maturity=maturity)
        return df
    
    def plot_yield_slider(self,i):
    
        trace = go.Scatter(x=self.curves.columns.tolist(), y=self.curves.loc[i].values, mode='markers', name=i)

        # Combine the scatter traces
        data = [trace]

        # Customize the scatter plot
        layout = go.Layout(
            title='Yield Curve',
            xaxis=dict(title='Maturities (Years)'),
            yaxis=dict(title='Yield Rates (%)'),
        )

        # Create the figure
        fig = go.Figure(data=data, layout=layout)

        # Display the scatter plot
        #fig.show()
        return fig
    @property
    def plot_yield_curve(self,interval='monthly'):
        """
        df: yeild curves
        """

        current = self.curves.iloc[-1]
        c_3 = self.curves.iloc[-3]
        c_6 = self.curves.iloc[-6]
        c_12 = self.curves.iloc[-12]

        # Sample data for yield curve
        maturities = current.index  # Example maturities in years

        # Sample yield rates for different time periods
        yield_rates_current = current.values  # Example yield rates for 1 year
        yield_rates_1yr = c_3.values  # Example yield rates for 1 year
        yield_rates_5yr = c_6.values  # Example yield rates for 5 years
        yield_rates_10yr = c_12.values  # Example yield rates for 10 years

        # Create the scatter traces for each time period
        trace_current = go.Scatter(x=maturities, y=yield_rates_current, mode='markers', name='Today')
        trace_1yr = go.Scatter(x=maturities, y=yield_rates_1yr, mode='markers', name='-3 months')
        trace_5yr = go.Scatter(x=maturities, y=yield_rates_5yr, mode='markers', name='-6 months')
        trace_10yr = go.Scatter(x=maturities, y=yield_rates_10yr, mode='markers', name='-12 months')

        # Combine the scatter traces
        data = [trace_current,trace_1yr, trace_5yr, trace_10yr]

        # Customize the scatter plot
        layout = go.Layout(
            title='Yield Curve',
            xaxis=dict(title='Maturities (Years)'),
            yaxis=dict(title='Yield Rates (%)'),
        )

        # Create the figure
        fig = go.Figure(data=data, layout=layout)

        # Display the scatter plot
        #fig.show()
        return fig
    
def main():

    self = MacroIndicators()
    # Sidebar date selection
    
    data = self.curves
    selected_date = st.sidebar.select_slider('Select a date', options=[d.strftime("%Y-%m-%d") for d in data.index],value=data.index[-1].strftime("%Y-%m-%d"))
    # # Filter data based on selected date
    # filtered_data = data.loc[selected_date]

    # # Plot data
    # fig = px.scatter(filtered_data, x='Date', y='value')

    # # Display the plot
    fig = self.plot_yield_slider(selected_date)
    st.plotly_chart(fig)
   

if __name__=='__main__':
    main()