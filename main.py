import pandas as pd
import numpy as np
from src.pricing_engine import BlackScholes
from src.data_loader import DataLoader
from src.visualization import plot_dashboard
from src.strategies import VolatilityStrategy # Upgraded
from src.risk_manager import RiskManager      # Upgraded
from src.backtester import Backtester

RISK_FREE_RATE = 0.07

def run_analysis():
    loader = DataLoader()
    
    # 1. Fetch Market Data
    nifty_data = loader.fetch_underlying_data(period="6mo")
    current_spot = nifty_data['Close'].iloc[-1]
    current_vol = nifty_data['Volatility'].iloc[-1]
    
    if isinstance(current_spot, pd.Series): current_spot = current_spot.item()
    if isinstance(current_vol, pd.Series): current_vol = current_vol.item()
        
    print(f"MARKET SNAPSHOT: Spot {current_spot:.0f} | Vol {current_vol:.2%}")
    
    # 2. Generate Chain & Simulate Noise
    chain = loader.generate_dummy_option_chain(current_spot, None)
    results = []
    
    print("\nSimulating Market Prices (Adding Random Noise)...")
    for index, row in chain.iterrows():
        bs = BlackScholes(row['Spot'], row['Strike'], row['Expiry_Days']/365, RISK_FREE_RATE, current_vol, 'call')
        theoretical_price = bs.calculate_price()
        
        # Random Noise (0.85 to 1.15)
        noise = np.random.uniform(0.85, 1.15)
        market_price = theoretical_price * noise
        
        implied_vol = bs.calculate_implied_volatility(market_price)

        results.append({
            'Spot': row['Spot'],
            'Strike': row['Strike'],
            'Market_Price': market_price,
            'Delta': bs.calculate_delta(),
            'Gamma': bs.calculate_gamma(),
            'Vega': bs.calculate_vega(),
            'Theta': bs.calculate_theta(),
            'Real_Vol': current_vol,
            'Implied_Vol': implied_vol
        })
        
    results_df = pd.DataFrame(results)
    
    # 3. RUN STRATEGY (Polynomial Fit + Straddles)
    strategy = VolatilityStrategy(volatility_threshold=0.015) 
    analyzed_df = strategy.generate_signals(results_df, current_spot)
    
    trades = strategy.get_trade_log(analyzed_df)
    
    print(f"\n--- ALGORITHMIC SIGNALS GENERATED: {len(trades)} ---")
    if not trades.empty:
        print(trades[['Strike', 'Market_Price', 'Implied_Vol', 'Fair_IV', 'Signal']].head().to_string(index=False))
        
        # 4. RUN RISK MANAGEMENT (Greeks + VaR + Stress Test)
        rm = RiskManager(lot_size=25)
        portfolio_risk = rm.calculate_portfolio_risk(trades)
        
        if portfolio_risk:
            print(f"\n=============================================")
            print(f"      RISK MANAGEMENT REPORT (CRO VIEW)      ")
            print(f"=============================================")
            print(f"NET DELTA: {portfolio_risk['Net_Delta']:.2f} (Directional Risk)")
            print(f"NET GAMMA: {portfolio_risk['Net_Gamma']:.4f} (Acceleration Risk)")
            print(f"NET VEGA:  {portfolio_risk['Net_Vega']:.2f} (Volatility Exposure)")
            print(f"NET THETA: {portfolio_risk['Net_Theta']:.2f} (Time Decay/Day)")
            print(f"---------------------------------------------")
            
            # VaR Calculation
            var = rm.calculate_var(portfolio_risk['Net_Delta'], current_spot, current_vol)
            print(f"VaR (1-Day, 95%): ₹{var:,.2f}")
            
            # Stress Test (-5% Crash)
            crash_pnl = rm.stress_test(portfolio_risk['Net_Delta'], portfolio_risk['Net_Gamma'], current_spot)
            print(f"STRESS TEST (-5% Crash): P&L Impact = ₹{crash_pnl:,.2f}")
            
            print(f"---------------------------------------------")
            print(f"HEDGE ACTION: {portfolio_risk['Futures_Hedge_Lots']} Lots of Nifty Futures")
            print(f"=============================================")

    # Save
    analyzed_df.to_csv("data/option_chain_output.csv", index=False)
    # ... previous code inside run_analysis ...
    print("\nData saved. Launching Dashboard...")
    
    # --- NEW: RUN BACKTEST ON FETCHED DATA ---
    from src.backtester import Backtester
    
    print("\n---------------------------------------------")
    print(">>> STARTING HISTORICAL BACKTEST (6 Months) <<<")
    bt = Backtester(initial_capital=1000000)
    
    equity_df = bt.run_backtest(nifty_data)
    
    # --- NEW: SAVE RESULTS FOR DASHBOARD ---
    equity_df.to_csv("data/backtest_results.csv", index=False)
    print("Backtest results saved to data/backtest_results.csv")
    
    final_equity = equity_df['Equity'].iloc[-1]
    roi = ((final_equity - 1000000) / 1000000) * 100
    
    print(f"Final Portfolio Value: ₹{final_equity:,.2f}")
    print(f"Total ROI: {roi:.2f}%")
    print("---------------------------------------------")
    
    # Launch Dashboard
    plot_dashboard()
    

if __name__ == "__main__":
    run_analysis()