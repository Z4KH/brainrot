import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from experiments.config import STOCK_NAME, COMPANY_NAME

INIT = True

class PortfolioTracker:
    def __init__(self, initial_balance=1000000.00):
        """Initialize the portfolio tracker with an initial balance."""
        self.portfolio_file = Path(f"experiments/results/{STOCK_NAME}/portfolio.json")
        self.performance_file = Path(f"experiments/results/{STOCK_NAME}/performance.csv")
        self.history_file = Path(f"experiments/results/{STOCK_NAME}/trading_history.json")
        self.portfolio_file.parent.mkdir(parents=True, exist_ok=True)
        
        
        if self.portfolio_file.exists() and not INIT:
            with open(self.portfolio_file, 'r') as f:
                data = json.load(f)
                self.portfolio = data['portfolio']
                self.balance = data['balance']
        else:
            self.portfolio = {} 
            self.balance = initial_balance
            self._save_portfolio()
        
        if not self.performance_file.exists() or INIT:
            self.performance_df = pd.DataFrame(columns=['date', 'net_worth'])
            self.performance_df.to_csv(self.performance_file, index=False)
        else:
            self.performance_df = pd.read_csv(self.performance_file)
            
        # Initialize or load trading history
        if self.history_file.exists() and not INIT:
            with open(self.history_file, 'r') as f:
                self.trading_history = json.load(f)
        else:
            self.trading_history = []
            self._save_history()

    def _save_portfolio(self):
        """Save the current portfolio state to file."""
        with open(self.portfolio_file, 'w') as f:
            json.dump({
                'portfolio': self.portfolio,
                'balance': self.balance
            }, f, indent=2)
            
    def _save_history(self):
        """Save the trading history to file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.trading_history, f, indent=2)

    def update_portfolio(self, asset, position, current_price, quantity, date):
        """
        Update portfolio based on agent's response.
        
        Args:
            asset (str): Asset name
            position (str): Position ('buy'/'sell'/'wait')
            current_price (float): Current price of the asset
            quantity (int): Number of shares to buy/sell
            date (str): Date of the transaction
        """
        
        # Record the trading decision in history
        decision_record = {
            'timestamp': date,
            'position': position,
            'asset': asset,
            'price': current_price,
            'quantity': quantity,
            'balance_before': self.balance,
            'portfolio_before': self.portfolio.copy()
        }
        
        if position == 'wait':
            decision_record['action_taken'] = 'wait'
            self.trading_history.append(decision_record)
            self._save_history()
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
                decision_record['action_taken'] = 'buy'
                decision_record['cost'] = cost
                    
        elif position == 'sell':
            if asset in self.portfolio:
                if quantity >= self.portfolio[asset]['quantity']:
                    # Sell all shares
                    revenue = self.portfolio[asset]['quantity'] * current_price
                    self.balance += revenue
                    del self.portfolio[asset]
                    decision_record['action_taken'] = 'sell_all'
                    decision_record['revenue'] = revenue
                else:
                    # Sell partial shares
                    revenue = quantity * current_price
                    self.balance += revenue
                    self.portfolio[asset]['quantity'] -= quantity
                    decision_record['action_taken'] = 'sell_partial'
                    decision_record['revenue'] = revenue
        
        decision_record['balance_after'] = self.balance
        decision_record['portfolio_after'] = self.portfolio.copy()
        self.trading_history.append(decision_record)
        
        self._save_portfolio()
        self._save_history()

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