import pandas as pd
import numpy as np
from scipy.stats import norm

class RiskManager:
    def __init__(self, lot_size=25, portfolio_value=1000000):
        self.lot_size = lot_size
        self.portfolio_value = portfolio_value # Capital allocated (e.g., 10 Lakhs)

    def calculate_portfolio_risk(self, trades_df):
        """
        Aggregates risk metrics across all active trades.
        """
        if trades_df.empty:
            return None

        # Initialize Totals
        net_delta = 0
        net_gamma = 0
        net_vega = 0
        net_theta = 0
        
        print("\n--- DETAILED RISK MONITOR ---")
        
        for index, row in trades_df.iterrows():
            # Determine Direction (+1 for Long, -1 for Short)
            if "Long" in row['Trade_Type']:
                direction = 1
            elif "Short" in row['Trade_Type']:
                direction = -1
            else:
                continue

            # Check if it's a Straddle (Double the risk: Call + Put)
            multiplier = 2 if "Straddle" in row['Trade_Type'] else 1
            
            # Sum up Greeks (Direction * Greek * LotSize * Multiplier)
            net_delta += direction * row['Delta'] * self.lot_size * multiplier
            net_gamma += direction * row['Gamma'] * self.lot_size * multiplier
            net_vega  += direction * row['Vega']  * self.lot_size * multiplier
            net_theta += direction * row['Theta'] * self.lot_size * multiplier

        # --- HEDGE CALCULATION (Delta Neutrality) ---
        futures_needed = -net_delta
        futures_lots = round(futures_needed / self.lot_size)

        return {
            'Net_Delta': net_delta,
            'Net_Gamma': net_gamma,
            'Net_Vega': net_vega,
            'Net_Theta': net_theta,
            'Futures_Hedge_Lots': futures_lots
        }

    def calculate_var(self, net_delta, current_price, volatility, confidence=0.95):
        """
        Parametric VaR (Value at Risk).
        Estimates max 1-day loss due to directional moves (Delta Risk).
        Formula: Exposure * Z-score * Daily_Vol
        """
        # Exposure in Rupee Terms = Net Delta * Spot Price
        exposure = net_delta * current_price
        
        # Z-score for 95% confidence (1.65) or 99% (2.33)
        z_score = norm.ppf(confidence)
        
        # Daily Volatility = Annual Vol / sqrt(252)
        daily_vol = volatility / np.sqrt(252)
        
        var_1day = abs(exposure * z_score * daily_vol)
        return var_1day

    def stress_test(self, net_delta, net_gamma, spot_price, drop_percent=0.05):
        """
        Estimates P&L if market drops by X% (e.g., 5%).
        Uses Delta-Gamma approximation: PnL = (Delta * dS) + (0.5 * Gamma * dS^2)
        """
        dS = spot_price * -drop_percent # Price change
        
        pnl_delta = net_delta * dS
        pnl_gamma = 0.5 * net_gamma * (dS ** 2)
        
        total_stress_pnl = pnl_delta + pnl_gamma
        return total_stress_pnl