import pandas as pd
import numpy as np
from src.pricing_engine import BlackScholes
from src.strategies import VolatilityStrategy
from src.risk_manager import RiskManager

class Backtester:
    def __init__(self, initial_capital=1000000):
        self.capital = initial_capital
        self.balance = initial_capital
        self.positions = [] # List of active trades
        self.equity_curve = []
        self.transaction_log = []
        
        # Costs
        self.brokerage_per_order = 20 # Flat fee (e.g., Zerodha)
        self.slippage_pct = 0.001     # 0.1% impact on entry/exit

    def run_backtest(self, price_data):
        """
        Simulates trading over a historical price series.
        """
        print(f"Starting Backtest with ₹{self.capital:,.2f}...")
        
        strategy = VolatilityStrategy(volatility_threshold=0.015)
        
        for i, row in price_data.iterrows():
            # --- SCALAR FIX STARTS HERE ---
            current_spot = row['Close']
            current_vol = row['Volatility']
            
            # Force conversion to simple float if it's a Series or Array
            if isinstance(current_spot, pd.Series):
                current_spot = current_spot.iloc[0]
            if isinstance(current_vol, pd.Series):
                current_vol = current_vol.iloc[0]
                
            # Double check it's not a numpy scalar
            if hasattr(current_spot, 'item'):
                current_spot = current_spot.item()
            if hasattr(current_vol, 'item'):
                current_vol = current_vol.item()
            # --- SCALAR FIX ENDS HERE ---

            date = row.index if isinstance(row.index, pd.Timestamp) else i
            
            # 1. Update Value of Existing Positions (Mark-to-Market)
            self._update_positions(current_spot, current_vol)
            
            # 2. Check for Exits
            self._check_exits(current_spot)
            
            # 3. Generate New Entry Signals
            atm_strike = round(current_spot / 50) * 50
            
            # Simulate Option Price
            bs = BlackScholes(current_spot, atm_strike, 25/365, 0.07, current_vol, 'call')
            theo_price = bs.calculate_price()
            
            # Create a dummy row for strategy
            dummy_row = pd.DataFrame([{
                'Strike': atm_strike, 'Implied_Vol': current_vol, 
                'Market_Price': theo_price, 'Real_Vol': current_vol
            }])
            
            # Run Strategy
            signals = strategy.generate_signals(dummy_row, current_spot)
            trade_signal = signals.iloc[0]['Signal']
            
            # 4. Execute Trade
            if "BUY" in trade_signal and len(self.positions) == 0:
                self._execute_trade("BUY", atm_strike, theo_price, date)
            elif "SELL" in trade_signal and len(self.positions) == 0:
                self._execute_trade("SELL", atm_strike, theo_price, date)
                
            # Track Equity
            total_equity = self.balance + sum(p['PnL'] for p in self.positions)
            self.equity_curve.append({'Date': date, 'Equity': total_equity})
            
        return pd.DataFrame(self.equity_curve)

    def _execute_trade(self, side, strike, price, date):
        qty = 25 # 1 Lot
        cost = price * qty
        slippage = cost * self.slippage_pct
        total_cost = self.brokerage_per_order + slippage
        
        self.balance -= total_cost
        
        self.positions.append({
            'Entry_Date': date,
            'Type': side,
            'Strike': strike,
            'Entry_Price': price,
            'Qty': qty,
            'PnL': 0
        })
        self.transaction_log.append(f"{date}: {side} {strike} Call @ {price:.2f}")

    def _update_positions(self, spot, vol):
        for pos in self.positions:
            bs = BlackScholes(spot, pos['Strike'], 20/365, 0.07, vol, 'call')
            curr_price = bs.calculate_price()
            
            if pos['Type'] == 'BUY':
                pos['PnL'] = (curr_price - pos['Entry_Price']) * pos['Qty']
            else:
                pos['PnL'] = (pos['Entry_Price'] - curr_price) * pos['Qty']

    def _check_exits(self, spot):
        active_pos = []
        for pos in self.positions:
            # Profit Target: 2000 | Stop Loss: -1000
            if pos['PnL'] > 2000 or pos['PnL'] < -1000:
                self.balance += pos['PnL']
            else:
                active_pos.append(pos)
        self.positions = active_pos