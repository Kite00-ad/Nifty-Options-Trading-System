import pandas as pd
import numpy as np
from src.pricing_engine import BlackScholes
from src.data_loader import DataLoader
from src.visualization import plot_dashboard
from src.strategies import VolatilityStrategy # <--- NEW IMPORT

# 1. Setup
RISK_FREE_RATE = 0.07

def run_analysis():
    loader = DataLoader()
    
    # Fetch Data
    nifty_data = loader.fetch_underlying_data(period="6mo")
    current_spot = nifty_data['Close'].iloc[-1]
    current_vol = nifty_data['Volatility'].iloc[-1]
    
    # Scalar fix
    if isinstance(current_spot, pd.Series): current_spot = current_spot.item()
    if isinstance(current_vol, pd.Series): current_vol = current_vol.item()
        
    print(f"MARKET SNAPSHOT: Spot {current_spot:.0f} | Vol {current_vol:.2%}")
    
    chain = loader.generate_dummy_option_chain(current_spot, None)
    results = []
    
    print("\nSimulating Market Prices (adding random noise)...")
    
    for index, row in chain.iterrows():
        bs = BlackScholes(row['Spot'], row['Strike'], row['Expiry_Days']/365, RISK_FREE_RATE, current_vol, 'call')
        
        theoretical_price = bs.calculate_price()
        
        # --- SIMULATION: Randomly mess up the market prices ---
        # Some options will be 20% expensive, some 20% cheap
        noise = np.random.uniform(0.80, 1.20) 
        market_price = theoretical_price * noise
        
        # Calculate IV based on this messy market price
        implied_vol = bs.calculate_implied_volatility(market_price)

        results.append({
            'Spot': row['Spot'],
            'Strike': row['Strike'],
            'Price': theoretical_price,
            'Market_Price': market_price, # The "noisy" price
            'Delta': bs.calculate_delta(),
            'Gamma': bs.calculate_gamma(),
            'Vega': bs.calculate_vega(),
            'Real_Vol': current_vol,
            'Implied_Vol': implied_vol
        })
        
    results_df = pd.DataFrame(results)
    
    # --- STEP 4: RUN THE STRATEGY ENGINE ---
    strategy = VolatilityStrategy(volatility_threshold=0.01) # 1% edge required
    analyzed_df = strategy.generate_signals(results_df)
    
    trades = strategy.get_trade_log(analyzed_df)
    
    print(f"\n--- TRADING SIGNALS FOUND: {len(trades)} ---")
    if not trades.empty:
        # Show top 5 trades
        print(trades[['Strike', 'Market_Price', 'Real_Vol', 'Implied_Vol', 'Signal']].head().to_string(index=False))
    
    # Save & Plot
    analyzed_df.to_csv("data/option_chain_output.csv", index=False)
    print("\nData saved. Launching Dashboard...")
    plot_dashboard()

if __name__ == "__main__":
    run_analysis()