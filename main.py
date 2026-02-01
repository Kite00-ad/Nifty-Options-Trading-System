import pandas as pd
from src.pricing_engine import BlackScholes
from src.data_loader import DataLoader

# 1. Setup
RISK_FREE_RATE = 0.07  # Assume 7% for India

def run_analysis():
    # Initialize Loader
    loader = DataLoader()
    
    # Fetch real market data
    nifty_data = loader.fetch_underlying_data(period="6mo")
    current_spot = nifty_data['Close'].iloc[-1]
    current_vol = nifty_data['Volatility'].iloc[-1]
    
    # YFinance fix: Extract scalar value if it's a Series
    if isinstance(current_spot, pd.Series):
        current_spot = current_spot.item()
    if isinstance(current_vol, pd.Series):
        current_vol = current_vol.item()
        
    print(f"MARKET SNAPSHOT:")
    print(f"Spot Price: {current_spot:.2f}")
    print(f"Volatility: {current_vol:.2%}")
    
    # Generate an Option Chain
    chain = loader.generate_dummy_option_chain(current_spot, None)
    
    # Calculate Prices and Greeks for every strike in the chain
    results = []
    
    for index, row in chain.iterrows():
        bs = BlackScholes(
            S=row['Spot'],
            K=row['Strike'],
            T=row['Expiry_Days'] / 365,
            r=RISK_FREE_RATE,
            sigma=current_vol,
            type='call'
        )
        
        results.append({
            'Strike': row['Strike'],
            'Price': bs.calculate_price(),
            'Delta': bs.calculate_delta(),
            'Gamma': bs.calculate_gamma(),
            'Theta': bs.calculate_theta(),
            'Vega': bs.calculate_vega()
        })
        
    results_df = pd.DataFrame(results)
    print("\n--- CALCULATED OPTION CHAIN (ATM) ---")
    
    # Find the row closest to ATM (At The Money)
    atm_row = results_df.iloc[(results_df['Strike'] - current_spot).abs().argsort()[:1]]
    print(atm_row.to_string(index=False))
    
    # Save to CSV so we can inspect it
    results_df.to_csv("data/option_chain_output.csv", index=False)
    print("\nFull chain saved to data/option_chain_output.csv")

if __name__ == "__main__":
    run_analysis()