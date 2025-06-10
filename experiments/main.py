"""
This file runs the experiment for a single stock using the data in data.py
and stock prices in prices.csv.

It runs the experiment from the start of the data(2025-05-01) to the end(2025-05-31). After every day, it passes
all data from that day and past days into the debate layer, which then decides
on what to do with the portfolio. The debate layer then passes the decision to
the portfolio tracker, which then updates the portfolio and balance.
"""
import json
import sys
import io
import pandas as pd
from datetime import datetime, timedelta

# Set console encoding to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from data.NVDA_news import data
from experiments.portfolio_tracker import PortfolioTracker
from debate.debate import Debate
from experiments.prompts import Prompts
from experiments.utils import Utils
from reasoning.llm import LLM
from experiments.config import STOCK_NAME, COMPANY_NAME, NUM_DAYS_PRICE_HISTORY, NUM_LAYERS, NUM_ROUNDS

import pandas as pd

def get_most_recent_close(csv_path, symbol, target_date_str):
    # Load CSV and parse date column
    df = pd.read_csv(csv_path, parse_dates=['date'])

    # Convert target date
    target_date = pd.to_datetime(target_date_str)

    # Filter for the given symbol and dates on or before target
    df_filtered = df[(df['symbol'] == symbol) & (df['date'] <= target_date)]

    # Sort by date descending to get the most recent first
    df_filtered = df_filtered.sort_values('date', ascending=False)

    # Return the first match if available
    if not df_filtered.empty:
        most_recent_row = df_filtered.iloc[0]
        return float(most_recent_row['close'])
    else:
        raise ValueError(f"No price exists before target date {target_date_str} for {symbol}")


def main():
    # Run an experiment with the data
    # Sort the data by date -- create a dict entry for each date
    sorted_data = {}
    for item in data:
        # Date is in iso format and includes the time as well
        date = item['date'].split('T')[0]
        
        if date not in sorted_data:
            sorted_data[date] = []
        sorted_data[date].append(item)
    
    # Then create a portfolio tracker instance
    portfolio_tracker = PortfolioTracker()
    
    # # Run the experiment
    llm = LLM()
    prompts = Prompts(STOCK_NAME, COMPANY_NAME, portfolio_tracker, current_date=None, current_price=None)
    utils = Utils()
    dates = sorted(sorted_data.keys())
    for date in dates:
        # Start from 2025-05-15
        if date < "2025-05-15":
            continue
        
        # Update prompts current date and price
        prompts.current_date = date
        current_price = get_most_recent_close(f"experiments/prices.csv", STOCK_NAME, date)
        prompts.current_price = current_price
        
        items = sorted_data[date]
        total_data = []
        # Get the last five days of data (date is a string in iso format)
        for i in range(NUM_DAYS_PRICE_HISTORY):
            formatted_date = datetime.strptime(date, "%Y-%m-%d")
            new_date = formatted_date - timedelta(days=i)
            new_date_str = new_date.strftime("%Y-%m-%d")
            if new_date_str in sorted_data:
                total_data.extend(sorted_data[new_date_str])
                
        print(f"Running experiment for {date} with {len(total_data)} data entries")
        
        debate = Debate(STOCK_NAME, total_data, prompts, utils, llm)
        # Pass the data to the debate layer
        debate.initialize(num_static_agents=5)
        decision = debate.run_debate(num_rounds=NUM_ROUNDS, num_hidden_layers=NUM_LAYERS)
        debate_output = debate.get_debate()
        with open(f"experiments/results/{STOCK_NAME}/debates/{date}.txt", "w") as f:
            f.write(debate_output)
        
        # Pass the decision to the portfolio tracker
        portfolio_tracker.update_portfolio(COMPANY_NAME, decision['position'].lower(), current_price, int(decision['quantity']), date)
        current_prices = {COMPANY_NAME: current_price}
        portfolio_tracker.update_performance(date, current_prices)

    
    
    

if __name__ == "__main__":
    main()
