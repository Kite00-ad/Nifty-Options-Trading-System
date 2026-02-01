# 📈 Nifty Options Algorithmic Trading System

A comprehensive Quantitative Trading Engine for Indian Equity Derivatives (Nifty 50). This system integrates real-time options pricing, volatility arbitrage strategies, dynamic delta hedging, and risk management (VaR/CVaR) into a unified dashboard.

![Dashboard Preview](https://via.placeholder.com/1000x500?text=Dashboard+Preview+placeholder) 
*(Note: Replace this with a screenshot of your actual Streamlit Dashboard)*

---

## 🚀 Key Features

### 1. 🧠 Options Pricing Engine (`src/pricing_engine.py`)
* **Black-Scholes-Merton Model:** Custom implementation for European options.
* **Greeks Calculation:** Real-time computation of Delta, Gamma, Theta, Vega, and Rho.
* **Implied Volatility Solver:** Newton-Raphson algorithm to reverse-engineer market IV from prices, with arbitrage violation safeguards.

### 2. ⚡ Strategy Modules (`src/strategies.py`)
* **Volatility Arbitrage:** Detects statistical mispricing between Implied Volatility (IV) and Realized Volatility (RV).
* **Smile/Skew Analysis:** Polynomial curve fitting to identify "cheap" or "expensive" strikes relative to the volatility surface.
* **Straddle Logic:** Automated signals for VIX mean reversion strategies.

### 3. 🛡️ Risk Management System (`src/risk_manager.py`)
* **Dynamic Delta Hedging:** Auto-calculates the required number of Nifty Futures to neutralize directional risk.
* **Portfolio Greeks:** Aggregated exposure metrics (Net Gamma, Net Vega).
* **VaR (Value at Risk):** Parametric estimation of 1-Day 95% confidence potential loss.
* **Stress Testing:** Scenario analysis for market crashes (-5% moves).

### 4. 🧪 Historical Backtester (`src/backtester.py`)
* **Event-Driven Engine:** Replays historical market data to validate strategies.
* **Realistic Costs:** Models slippage (0.1%) and brokerage fees to simulate real-world P&L.
* **Mark-to-Market:** Daily equity curve tracking.

### 5. 📊 Interactive Dashboard (`app.py`)
* Built with **Streamlit** & **Plotly**.
* Real-time "Chief Risk Officer" (CRO) view of portfolio health.
* Interactive scenario analysis (slide Spot Price to see P&L changes).

---

## 🛠️ Tech Stack
* **Language:** Python 3.9+
* **Libraries:** `pandas`, `numpy`, `scipy` (Optimization), `plotly` (Visualization), `yfinance` (Data), `streamlit` (UI).

---

## 💻 How to Run Locally

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/Kite00-ad/Nifty-Options-Trading-System.git](https://github.com/Kite00-ad/Nifty-Options-Trading-System.git)
    cd Nifty-Options-Trading-System
    ```

2.  **Set up Virtual Environment**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install numpy pandas scipy yfinance plotly streamlit
    ```

4.  **Run the System**
    ```bash
    # Run the Analysis & Backtest
    python main.py

    # Launch the Dashboard
    streamlit run app.py
    ```

---

## 📉 Example Backtest Result
* **Strategy:** Volatility Arbitrage (Long/Short IV outliers)
* **Period:** 6 Months (Nifty 50)
* **Initial Capital:** ₹10,00,000
* **ROI:** -3.91% (Demonstrates impact of Slippage & Transaction Costs)

---

## ⚠️ Disclaimer
*This project is for educational purposes only. It is not financial advice. Algorithmic trading involves significant risk.*