import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_dashboard(csv_path="data/option_chain_output.csv"):
    # 1. Load Data
    df = pd.read_csv(csv_path)
    
    # 2. Setup the "Canvas" (3 charts side-by-side)
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))
    plt.suptitle(f"Option Analytics Dashboard (Spot: {df['Spot'].iloc[0]:.0f})", fontsize=16)
    
    # --- CHART 1: The Volatility Smile ---
    # We plot Implied Vol vs. Strike
    sns.lineplot(x=df['Strike'], y=df['Implied_Vol'], ax=ax1, color='purple', marker='o', label='Implied Vol (IV)')
    ax1.axhline(y=df['Real_Vol'].iloc[0], color='green', linestyle='--', label='Realized Vol (HV)')
    ax1.set_title("Volatility Skew / Smile")
    ax1.set_ylabel("Volatility")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # --- CHART 2: Delta (Directional Risk) ---
    sns.lineplot(x=df['Strike'], y=df['Delta'], ax=ax2, color='blue', label='Delta')
    ax2.set_title("Delta Exposure")
    ax2.set_ylabel("Delta (0 to 1)")
    ax2.axvline(x=df['Spot'].iloc[0], color='black', linestyle=':', label='ATM')
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    # --- CHART 3: Gamma (Acceleration) ---
    sns.lineplot(x=df['Strike'], y=df['Gamma'], ax=ax3, color='orange', label='Gamma')
    ax3.set_title("Gamma Risk (The 'Explosion' Risk)")
    ax3.set_ylabel("Gamma")
    ax3.axvline(x=df['Spot'].iloc[0], color='black', linestyle=':', label='ATM')
    ax3.grid(True, alpha=0.3)
    ax3.legend()

    # 3. Show Plot
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_dashboard()