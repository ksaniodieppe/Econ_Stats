""""Web Based Exchange Rates and S&P 500 Dashboard"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import yfinance as yf
from datetime import datetime, timedelta

def main():
    st.title('Exchange Rates and S&P 500 Dashboard')
    
    # Sidebar for controls
    years_to_show = st.sidebar.slider('Years to Show', 1, 20, 10)
    
    # Calculate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years_to_show)
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')

    # Load data
    with st.spinner('Downloading data...'):
        # Get S&P 500 data
        sp500 = yf.download('^GSPC', start=start_str, end=end_str, progress=False, auto_adjust=True)
        sp500_df = pd.DataFrame(index=sp500.index)
        sp500_df['Close'] = sp500['Close']
        
        # Get exchange rate data
        url = f'https://api.frankfurter.app/{start_str}..{end_str}?from=EUR&to=USD,GBP'
        response = requests.get(url)
        data = response.json()
        
        df_rates = pd.DataFrame.from_dict(data['rates'], orient='index')
        df_rates.index = pd.to_datetime(df_rates.index)
        df_rates = df_rates.sort_index()
        
        # Align dates and calculate EUR values
        common_dates = sp500_df.index.intersection(df_rates.index)
        sp500_df = sp500_df.loc[common_dates]
        df_rates = df_rates.loc[common_dates]
        sp500_df['EUR'] = sp500_df['Close'] / df_rates['USD'].astype(float)

    # Create plots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    plt.subplots_adjust(hspace=0.3)

    # Plot 1: Exchange Rates
    ax1.plot(df_rates.index, df_rates['USD'], label='EUR/USD', color='blue', linewidth=1)
    ax1.plot(df_rates.index, df_rates['GBP'], label='EUR/GBP', color='red', linewidth=1)
    ax1.set_title('EUR Exchange Rates', fontsize=14)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Exchange Rate')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend()
    ax1.tick_params(axis='x', rotation=45)

    # Plot 2: S&P 500
    ax2.plot(sp500_df.index, sp500_df['Close'], label='S&P 500 (USD)', color='green', linewidth=1)
    ax2.plot(sp500_df.index, sp500_df['EUR'], label='S&P 500 (EUR)', color='purple', linewidth=1)
    ax2.set_title('S&P 500 Index', fontsize=14)
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Index Value')
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.legend()
    ax2.tick_params(axis='x', rotation=45)

    st.pyplot(fig)

if __name__ == '__main__':
    main()
