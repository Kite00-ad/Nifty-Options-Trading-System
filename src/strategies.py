import pandas as pd
import numpy as np

class VolatilityStrategy:
    def __init__(self, volatility_threshold=0.02, risk_free_rate=0.07):
        self.threshold = volatility_threshold
        self.r = risk_free_rate

    def fit_iv_smile(self, df):
        """
        STRATEGY A UPGRADE: Polynomial Curve Fitting.
        Instead of a flat threshold, we fit a 2nd-degree polynomial (Parabola)
        to the Implied Volatility to find the 'Fair Value' curve.
        """
        # Filter for valid IVs (remove 0s or errors)
        valid_data = df[df['Implied_Vol'] > 0.001].copy()
        
        if len(valid_data) < 3:
            return df # Not enough points to fit a curve
        
        # Fit a 2nd degree polynomial: IV = ax^2 + bx + c (where x is Strike)
        coeffs = np.polyfit(valid_data['Strike'], valid_data['Implied_Vol'], 2)
        curve_func = np.poly1d(coeffs)
        
        # Calculate 'Fair IV' for every strike
        df['Fair_IV'] = curve_func(df['Strike'])
        
        # Calculate the "Spread" (Actual IV - Fair IV)
        df['IV_Spread'] = df['Implied_Vol'] - df['Fair_IV']
        
        return df

    def generate_signals(self, df, current_spot):
        """
        Generates signals for Outliers (Strategy A) and Straddles (Strategy B).
        """
        # 1. Fit the Smile Curve first
        df = self.fit_iv_smile(df)
        
        signals = []
        trade_types = []
        
        # 2. Analyze each option
        for index, row in df.iterrows():
            iv = row['Implied_Vol']
            fair_iv = row.get('Fair_IV', iv) # Default to IV if fit failed
            spread = row.get('IV_Spread', 0)
            
            signal = "HOLD"
            trade_type = "None"
            
            # --- STRATEGY A: OUTLIER DETECTION (Relative to Curve) ---
            # If Implied Vol is significantly higher than the Fitted Curve -> Sell
            if spread > self.threshold:
                signal = "SELL_VOL (Overpriced)"
                trade_type = "Short Call" # Simplifying to Calls for now
            
            # If Implied Vol is significantly lower -> Buy
            elif spread < -self.threshold:
                signal = "BUY_VOL (Cheap)"
                trade_type = "Long Call"

            # --- STRATEGY B: ATM STRADDLE LOGIC (VIX Mean Reversion) ---
            # If this is the ATM Strike (closest to Spot)
            if abs(row['Strike'] - current_spot) < 25:
                # If IV is historically LOW (< 12%), Buy Straddle (Bet on explosion)
                if iv < 0.12:
                    signal = "*** BUY STRADDLE (Low Vol)"
                    trade_type = "Long Straddle"
                # If IV is historically HIGH (> 20%), Sell Straddle (Bet on calm)
                elif iv > 0.20:
                    signal = "*** SELL STRADDLE (High Vol)"
                    trade_type = "Short Straddle"

            signals.append(signal)
            trade_types.append(trade_type)
            
        df['Signal'] = signals
        df['Trade_Type'] = trade_types
        return df

    def get_trade_log(self, df):
        return df[df['Signal'] != "HOLD"]