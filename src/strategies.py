import pandas as pd

class VolatilityStrategy:
    def __init__(self, volatility_threshold=0.02):
        """
        volatility_threshold: How much difference we need to trade.
        e.g., 0.02 means we only trade if IV is 2% different from HV.
        """
        self.threshold = volatility_threshold

    def generate_signals(self, df):
        """
        Scans the DataFrame for mispricing opportunities.
        Returns the DataFrame with a 'Signal' column.
        """
        signals = []
        
        for index, row in df.iterrows():
            iv = row['Implied_Vol']
            hv = row['Real_Vol']
            
            # Logic: Buy Low IV, Sell High IV
            if iv < (hv - self.threshold):
                signal = "BUY_VOL (Undervalued)"
            elif iv > (hv + self.threshold):
                signal = "SELL_VOL (Overvalued)"
            else:
                signal = "HOLD (Fair Value)"
                
            signals.append(signal)
            
        df['Signal'] = signals
        return df

    def get_trade_log(self, df):
        """
        Returns only the rows where a trade signal exists.
        """
        return df[df['Signal'] != "HOLD (Fair Value)"]