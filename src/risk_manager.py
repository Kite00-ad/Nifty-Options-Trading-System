import pandas as pd

class HedgeCalculator:
    def __init__(self, lot_size=25): # Nifty Lot Size is typically 25 or 50
        self.lot_size = lot_size

    def calculate_hedge(self, trades_df):
        """
        Input: DataFrame of active trades with 'Signal' and 'Delta' columns.
        Output: A dictionary with the Net Delta and the required Futures trade.
        """
        if trades_df.empty:
            return None

        net_delta_share_terms = 0
        
        print("\n--- CALCULATING PORTFOLIO RISK ---")
        
        for index, row in trades_df.iterrows():
            # 1. Identify Position Size (1 Lot)
            # If we BUY, we own +Delta. If we SELL, we own -Delta.
            if "BUY" in row['Signal']:
                direction = 1  # Long
                print(f"Long  {row['Strike']} Call | Delta: {row['Delta']:.2f}")
            elif "SELL" in row['Signal']:
                direction = -1 # Short
                print(f"Short {row['Strike']} Call | Delta: {row['Delta']:.2f}")
            else:
                continue

            # Position Delta = Direction * Delta_per_unit * Lot_Size
            pos_delta = direction * row['Delta'] * self.lot_size
            net_delta_share_terms += pos_delta

        # 2. Calculate Hedge Requirement
        # To be Delta Neutral: Portfolio_Delta + Futures_Delta = 0
        # Futures Delta is 1.0. So we need: Futures = -Portfolio_Delta
        futures_exposure_needed = -net_delta_share_terms
        
        # Convert to Lots (Rounding to nearest whole lot)
        lots_to_trade = round(futures_exposure_needed / self.lot_size)
        
        return {
            'Net_Delta': net_delta_share_terms,
            'Futures_Needed_Qty': futures_exposure_needed,
            'Futures_Lots': lots_to_trade
        }