import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DataLoader:
    def __init__(self, ticker="^NSEI"):
        self.ticker = ticker
        
    def fetch_underlying_data(self, period="1y"):
        """
        Fetches historical data for the underlying asset (Nifty 50)
        """
        print(f"Fetching data for {self.ticker}...")
        data = yf.download(self.ticker, period=period)
        
        # Calculate daily returns and historical volatility (annualized)
        data['Returns'] = data['Close'].pct_change()
        data['Volatility'] = data['Returns'].rolling(window=21).std() * np.sqrt(252)
        
        return data.dropna()

    def generate_dummy_option_chain(self, spot_price, date):
        """
        Since free historical options data is rare, we SIMULATE an option chain
        based on the spot price for testing our strategies.
        """
        strikes = []
        # Create strikes +/- 5% around spot price, steps of 50
        center_strike = round(spot_price / 50) * 50
        for k in range(center_strike - 1000, center_strike + 1050, 50):
            strikes.append(k)
            
        # Create a DataFrame
        chain = pd.DataFrame({'Strike': strikes})
        chain['Spot'] = spot_price
        chain['Expiry_Days'] = 30  # Assume 30 days to expiry for this test
        chain['Type'] = 'Call'     # Focus on Calls first
        
        return chain