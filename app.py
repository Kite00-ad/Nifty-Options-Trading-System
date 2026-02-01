import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from src.pricing_engine import BlackScholes
from src.risk_manager import RiskManager

# Page Config
st.set_page_config(page_title="Nifty Quant Trader", layout="wide")
st.title("📊 Nifty Options Algo-Trader & Risk Engine")

# --- SIDEBAR: MARKET SIMULATOR ---
st.sidebar.header("Market Simulator")
spot_price = st.sidebar.number_input("Nifty Spot Price", value=24825, step=50)
volatility = st.sidebar.slider("Market Volatility (IV)", 0.05, 0.50, 0.11)
days_to_expiry = st.sidebar.slider("Days to Expiry", 1, 30, 25)

# --- BACKEND: GENERATE DATA ---
# Generate a chain centered around the user's selected Spot Price
strikes = range(int(spot_price/50)*50 - 1000, int(spot_price/50)*50 + 1000, 50)
chain_data = []

# Simulate 'Real' Portfolio: Let's assume we are Short Strangle (Selling OTM Calls/Puts)
# We will hardcode a hypothetical portfolio for demonstration
st.sidebar.subheader("Active Strategy")
strategy_type = st.sidebar.selectbox("Select Strategy", ["Long Call", "Short Straddle", "Iron Condor"])

portfolio_trades = []

# Logic to build dummy portfolio based on selection
if strategy_type == "Long Call":
    # Long ATM Call
    portfolio_trades.append({'Strike': int(spot_price/50)*50, 'Type': 'Call', 'Trade_Type': 'Long Call'})
elif strategy_type == "Short Straddle":
    # Short ATM Call & Put
    atm = int(spot_price/50)*50
    portfolio_trades.append({'Strike': atm, 'Type': 'Call', 'Trade_Type': 'Short Straddle'})
    portfolio_trades.append({'Strike': atm, 'Type': 'Put', 'Trade_Type': 'Short Straddle'})

# Calculate Metrics for the Portfolio
risk_data = []
for trade in portfolio_trades:
    bs = BlackScholes(spot_price, trade['Strike'], days_to_expiry/365, 0.07, volatility, type=trade['Type'].lower())
    price = bs.calculate_price()
    
    risk_data.append({
        'Strike': trade['Strike'],
        'Trade_Type': trade['Trade_Type'],
        'Price': price,
        'Delta': bs.calculate_delta(),
        'Gamma': bs.calculate_gamma(),
        'Vega': bs.calculate_vega(),
        'Theta': bs.calculate_theta()
    })

df_risk = pd.DataFrame(risk_data)

# --- RUN RISK MANAGER ---
rm = RiskManager(lot_size=25)
portfolio_risk = rm.calculate_portfolio_risk(df_risk)

# --- DASHBOARD LAYOUT ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Net Delta (Direction)", f"{portfolio_risk['Net_Delta']:.2f}", delta_color="inverse")
    
with col2:
    st.metric("Net Gamma (Explosion)", f"{portfolio_risk['Net_Gamma']:.4f}")
    
with col3:
    hedge_qty = portfolio_risk['Futures_Hedge_Lots']
    action = "BUY" if hedge_qty > 0 else "SELL"
    color = "normal" if hedge_qty == 0 else "off"
    st.metric("Hedge Recommendation", f"{action} {abs(hedge_qty)} Lots", delta_color=color)

# --- VISUALIZATION: PAYOFF DIAGRAM ---
st.subheader("Simulated P&L Payoff")
# Create a range of spot prices to simulate outcome
sim_spots = np.linspace(spot_price * 0.9, spot_price * 1.1, 50)
pnl_values = []

for s in sim_spots:
    pnl = 0
    for trade in portfolio_trades:
        # PnL = (New_Price - Entry_Price) * Direction
        # This is a simplified expiration payoff
        if trade['Type'] == 'Call':
            value = max(0, s - trade['Strike'])
        else:
            value = max(0, trade['Strike'] - s)
            
        entry = risk_data[0]['Price'] # Approximate entry as current price for visual
        direction = 1 if "Long" in trade['Trade_Type'] else -1
        pnl += direction * (value - entry) * 25 # Lot size
        
    pnl_values.append(pnl)

fig = go.Figure()
fig.add_trace(go.Scatter(x=sim_spots, y=pnl_values, mode='lines', name='P&L', fill='tozeroy'))
fig.add_vline(x=spot_price, line_dash="dash", line_color="white", annotation_text="Current Spot")
st.plotly_chart(fig, use_container_width=True)

# --- RISK REPORT ---
st.subheader("Risk Officer Report")
var = rm.calculate_var(portfolio_risk['Net_Delta'], spot_price, volatility)
crash_test = rm.stress_test(portfolio_risk['Net_Delta'], portfolio_risk['Net_Gamma'], spot_price)

r1, r2 = st.columns(2)
r1.error(f"VaR (1-Day 95%): ₹{var:,.2f}")
r2.warning(f"Stress Test (-5% Crash): ₹{crash_test:,.2f}")

# --- HISTORICAL BACKTEST RESULTS ---
st.markdown("---")
st.subheader("📜 Historical Backtest Performance (6 Months)")

try:
    backtest_df = pd.read_csv("data/backtest_results.csv")
    
    # Calculate Metrics
    initial_balance = 1000000
    final_balance = backtest_df['Equity'].iloc[-1]
    total_return = ((final_balance - initial_balance) / initial_balance) * 100
    
    # Metrics Row
    m1, m2, m3 = st.columns(3)
    m1.metric("Initial Capital", f"₹{initial_balance:,.0f}")
    m2.metric("Final Equity", f"₹{final_balance:,.2f}", delta=f"{total_return:.2f}%")
    
    # Draw Equity Curve
    fig_equity = go.Figure()
    fig_equity.add_trace(go.Scatter(
        x=backtest_df['Date'], 
        y=backtest_df['Equity'],
        mode='lines',
        name='Portfolio Value',
        line=dict(color='#00CC96', width=2)
    ))
    fig_equity.update_layout(
        title="Portfolio Equity Curve",
        xaxis_title="Date",
        yaxis_title="Equity (₹)",
        template="plotly_dark",
        height=400
    )
    st.plotly_chart(fig_equity, use_container_width=True)

except FileNotFoundError:
    st.warning("⚠️ No backtest data found. Run 'main.py' to generate results.")