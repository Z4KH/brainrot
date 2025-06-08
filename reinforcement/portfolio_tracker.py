import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

class PortfolioTracker:
    def __init__(self, initial_balance=1000000.00):
        """Initialize the portfolio tracker with an initial balance."""
        self.portfolio_file = Path("reinforcement/data/portfolio.json")
        self.performance_file = Path("reinforcement/data/performance.csv")
        self.portfolio_file.parent.mkdir(parents=True, exist_ok=True)
        
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r') as f:
                data = json.load(f)
                self.portfolio = data['portfolio']
                self.balance = data['balance']
        else:
            self.portfolio = {} 
            self.balance = initial_balance
            self._save_portfolio()
        
        if not self.performance_file.exists():
            self.performance_df = pd.DataFrame(columns=['date', 'net_worth'])
            self.performance_df.to_csv(self.performance_file, index=False)
        else:
            self.performance_df = pd.read_csv(self.performance_file)

    def _save_portfolio(self):
        """Save the current portfolio state to file."""
        with open(self.portfolio_file, 'w') as f:
            json.dump({
                'portfolio': self.portfolio,
                'balance': self.balance
            }, f, indent=2)

    def update_portfolio(self, agent_response, current_price, quantity):
        """
        Update portfolio based on agent's response.
        
        Args:
            agent_response (dict): Agent's trading decision with format:
                {
                    'position': 'Buy'/'Sell'/'Wait',
                    'asset': str,
                    'projected_percentage_change': float,
                    'time_horizon': int,
                    'confidence': float
                }
            current_price (float): Current price of the asset
            quantity (int): Number of shares to buy/sell
        """
        position = agent_response['position'].lower()
        asset = agent_response['asset']
        
        if position == 'wait':
            return
            
        if position == 'buy':
            cost = quantity * current_price
            if cost <= self.balance:
                if asset not in self.portfolio:
                    self.portfolio[asset] = {'price': current_price, 'quantity': quantity}
                else:
                    # Update average price
                    current_value = self.portfolio[asset]['price'] * self.portfolio[asset]['quantity']
                    new_value = current_price * quantity
                    total_quantity = self.portfolio[asset]['quantity'] + quantity
                    avg_price = (current_value + new_value) / total_quantity
                    self.portfolio[asset]['price'] = avg_price
                    self.portfolio[asset]['quantity'] = total_quantity
                
                self.balance -= cost
                    
        elif position == 'sell':
            if asset in self.portfolio:
                if quantity >= self.portfolio[asset]['quantity']:
                    # Sell all shares
                    revenue = self.portfolio[asset]['quantity'] * current_price
                    self.balance += revenue
                    del self.portfolio[asset]
                else:
                    # Sell partial shares
                    revenue = quantity * current_price
                    self.balance += revenue
                    self.portfolio[asset]['quantity'] -= quantity
        
        self._save_portfolio()

    def update_performance(self, timestamp, current_prices):
        """
        Update performance table with current net worth.
        
        Args:
            timestamp (str): Current timestamp
            current_prices (dict): Dictionary of current prices for each asset
        """
        # Calculate total portfolio value
        portfolio_value = sum(
            self.portfolio[asset]['quantity'] * current_prices.get(asset, self.portfolio[asset]['price'])
            for asset in self.portfolio
        )
        
        net_worth = self.balance + portfolio_value
        
        # Add new row to performance DataFrame
        new_row = pd.DataFrame([{
            'date': timestamp,
            'net_worth': net_worth
        }])
        
        self.performance_df = pd.concat([self.performance_df, new_row], ignore_index=True)
        self.performance_df.to_csv(self.performance_file, index=False)

    def get_portfolio_summary(self, asset, current_price, news_source=None, reliability=None):
        """
        Get a summary of the portfolio status for a specific asset.
        
        Args:
            asset (str): Asset name
            current_price (float): Current price of the asset
            news_source (str, optional): Source of the news
            reliability (str, optional): Reliability of the source
        
        Returns:
            str: Formatted summary string
        """
        if asset in self.portfolio:
            purchase_price = self.portfolio[asset]['price']
            quantity = self.portfolio[asset]['quantity']
            result = 'profit' if current_price > purchase_price else 'loss'
        else:
            purchase_price = 0
            quantity = 0
            result = 'n/a'
            
        summary = f"""
Portfolio Summary:
----------------
Stock: {asset}
Available Balance: ${self.balance:.2f}
Quantity Owned: {quantity}
Purchase Price: ${purchase_price:.2f}
Current Price: ${current_price:.2f}
"""
        
        if news_source and reliability:
            summary += f"""
News Source: {news_source}
Source Reliability: {reliability}
"""
            
        summary += f"Verdict: {result}"
        
        return summary 