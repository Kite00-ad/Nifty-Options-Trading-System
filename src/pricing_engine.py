import numpy as np
from scipy.stats import norm

class BlackScholes:
    def __init__(self, S, K, T, r, sigma, type='call'):
        self.S = S          # Spot Price
        self.K = K          # Strike Price
        self.T = T          # Time to Maturity (years)
        self.r = r          # Risk-free Rate
        self.sigma = sigma  # Volatility
        self.type = type    # 'call' or 'put'

    def _calculate_d1_d2(self):
        d1 = (np.log(self.S / self.K) + (self.r + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * np.sqrt(self.T))
        d2 = d1 - self.sigma * np.sqrt(self.T)
        return d1, d2

    def calculate_price(self):
        d1, d2 = self._calculate_d1_d2()
        if self.type == 'call':
            return (self.S * norm.cdf(d1)) - (self.K * np.exp(-self.r * self.T) * norm.cdf(d2))
        else:
            return (self.K * np.exp(-self.r * self.T) * norm.cdf(-d2)) - (self.S * norm.cdf(-d1))

    # --- THE GREEKS (Risk Metrics) ---
    
    def calculate_delta(self):
        # Delta: How much option price changes for a 1 point move in the underlying stock
        d1, _ = self._calculate_d1_d2()
        if self.type == 'call':
            return norm.cdf(d1)
        else:
            return norm.cdf(d1) - 1

    def calculate_gamma(self):
        # Gamma: How fast Delta changes (Acceleration of the price)
        # Same for calls and puts
        d1, _ = self._calculate_d1_d2()
        return norm.pdf(d1) / (self.S * self.sigma * np.sqrt(self.T))

    def calculate_vega(self):
        # Vega: Sensitivity to Volatility (Critical for IV strategies)
        # Same for calls and puts
        d1, _ = self._calculate_d1_d2()
        return self.S * norm.pdf(d1) * np.sqrt(self.T) / 100  # Divided by 100 to show per 1% vol change

    def calculate_theta(self):
        # Theta: Time decay (How much value you lose per day)
        d1, d2 = self._calculate_d1_d2()
        term1 = -(self.S * norm.pdf(d1) * self.sigma) / (2 * np.sqrt(self.T))
        
        if self.type == 'call':
            term2 = self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
            theta = term1 - term2
        else:
            term2 = self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(-d2)
            theta = term1 + term2
            
        return theta / 365  # Return daily decay

    def calculate_rho(self):
        # Rho: Sensitivity to Interest Rates
        _, d2 = self._calculate_d1_d2()
        if self.type == 'call':
            return self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(d2) / 100
        else:
            return -self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-d2) / 100
        
    def calculate_implied_volatility(self, market_price):
        """
        Calculates Implied Volatility (IV) using Newton-Raphson method.
        We guess a volatility, check the price error, and adjust using Vega.
        """
        MAX_ITERATIONS = 100
        PRECISION = 1.0e-5
        
        # Start with a guess (e.g., 50% volatility)
        sigma = 0.5
        
        for i in range(MAX_ITERATIONS):
            # 1. Update our internal sigma to the guess
            self.sigma = sigma
            
            # 2. Calculate price and vega with this sigma
            price = self.calculate_price()
            vega = self.calculate_vega() * 100  # Remove the /100 scaling for the math to work
            
            # 3. How far off are we?
            diff = market_price - price
            
            if abs(diff) < PRECISION:
                return sigma
            
            # 4. Newton-Raphson Step: Adjust guess
            # Avoid division by zero if vega is tiny
            if abs(vega) < 1e-8:
                return sigma 
                
            sigma = sigma + (diff / vega)
            
        return sigma # Return best guess if we hit max iterations

if __name__ == "__main__":
    # Test Case: Nifty ATM Option
    S = 24000; K = 24000; T = 30/365; r = 0.07; sigma = 0.15
    
    bs = BlackScholes(S, K, T, r, sigma, type='call')
    
    print(f"--- Nifty Call Option (Strike: {K}) ---")
    print(f"Price: {bs.calculate_price():.2f}")
    print(f"Delta: {bs.calculate_delta():.4f} (Speed)")
    print(f"Gamma: {bs.calculate_gamma():.4f} (Acceleration)")
    print(f"Vega:  {bs.calculate_vega():.4f} (Exposure to 1% Vol change)")
    print(f"Theta: {bs.calculate_theta():.4f} (Daily Time Decay)")