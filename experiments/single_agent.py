"""
This file runs a monthlong experiment with a single agent.
The agent handles all the data and makes decisions based on the data by itself at each timestep
in one prompt.
"""

import json
import sys
import io
import pandas as pd
from datetime import datetime, timedelta

# Set console encoding to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from data.TSLA_news import data
from experiments.portfolio_tracker import PortfolioTracker
from debate.debate import Debate
from experiments.prompts import Prompts
from experiments.utils import Utils
from reasoning.llm import LLM
from experiments.config import STOCK_NAME, COMPANY_NAME, NUM_DAYS_PRICE_HISTORY, NUM_LAYERS, NUM_ROUNDS

import pandas as pd

def get_price_history(stock_name, current_date) -> str:
        """
        Get the price history.
        
        :param stock_name: The stock name
        :param current_date: The current date
        :return: The price history
        """
        # Load CSV and parse dates
        df = pd.read_csv(f"experiments/prices.csv", parse_dates=['date'])

        # Filter for the given symbol and sort by date
        df = df[df['symbol'] == stock_name].sort_values('date')

        # Convert target date
        target_date = pd.to_datetime(current_date)

        # Get all dates <= target date
        df_filtered = df[df['date'] <= target_date]

        # Get last up to 5 rows
        last_rows = df_filtered.tail(5)

        # Format to string: MM-DD-YYYY: $price
        lines = [
            f"{row['date'].strftime('%m-%d-%Y')}: ${row['close']:.2f}"
            for _, row in last_rows.iterrows()
        ]

        return "\n".join(lines)

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
        
        portfolio_state = portfolio_tracker.get_portfolio_summary(COMPANY_NAME, current_price)
        price_history = get_price_history(STOCK_NAME, date)
        prompt = SINGLE_AGENT_PROMPT.format(company_name=COMPANY_NAME, stock_name=STOCK_NAME, current_date=date, data=total_data, portfolio_state=portfolio_state, price_history=price_history)
        output = llm.generate(llm.format_messages(prompt))
        with open(f"experiments/results/{STOCK_NAME}/single_agent/decisions/{date}.txt", "w", encoding='utf-8') as f:
            f.write(output)
            
        decision = utils.parse_agent_output(output)
        
        # Pass the decision to the portfolio tracker
        portfolio_tracker.update_portfolio(COMPANY_NAME, decision['position'].lower(), current_price, int(decision['quantity']), date)
        current_prices = {COMPANY_NAME: current_price}
        portfolio_tracker.update_performance(date, current_prices)

    
SINGLE_AGENT_PROMPT = """
You are TraderAgent, an autonomous financial decision-making agent for a high-stakes trading benchmark.

Your task is to evaluate **{company_name} (ticker: {stock_name})** as a short-term trading opportunity and issue a **final, irreversible trading recommendation** based entirely on the provided data.

Your output will directly determine the trading action. There is **no external review or correction**.

Do not be afraid to take risks.

---

### Context

- **Date:** {current_date}
- **Time Horizon:** 1 day (until market close tomorrow)
- **Asset:** {company_name} (ticker: {stock_name})

You are provided with:
- The **current portfolio state**
- **Recent stock price history**
- **Structured input data** relevant to your expertise

---

### Portfolio State

{portfolio_state}

---

### Recent Price History

{price_history}

---

### Final Responsibilities

You must:

- **Analyze** all structured data and market history with clarity and objectivity.
- **Synthesize** a single, definitive trading stance grounded in facts and evidence.
- Issue a **clear, confident recommendation** that will be executed as-is.

You must include:

- A trading **Position**: Buy, Sell, or Wait
- A **Projected Percentage Change** over 1 day (+/-X.X%)
- A **Confidence** score between 0.00 and 1.00
- A **Justification** strictly based on:
  - Structured data
  - Portfolio context
  - Price history

There will be **no further deliberation**. You are solely accountable for this decision.

---

### Output Format

Return your response using the following format **exactly**:

Justification:  
[Concise, data-grounded synthesis. Cite facts from structured data and price history.]

Position:  
[Buy / Sell / Wait]

Quantity:  
[Number of shares to buy or sell (0 if Wait) — must be a realistic integer based on current portfolio and price history]

Projected Percentage Change:  
[+/-X.X%]

Confidence:  
[0.00 to 1.00]

---

### Strict Do-Nots:

- Do **not** mention any asset other than {company_name}.
- Do **not** include a time horizon (it is fixed at 1 day).
- Do **not** invent data, quotes, or reasoning not present in your inputs.
- Do **not** hedge or remain undecided — you must take a clear stance.
- Do **not** defer responsibility.
- Do **not** deviate from the required output format.
- Do **not** be afraid to take risks.

---

### Structured Data  
{data}
---

Output your response in the specified format now.
"""

    

if __name__ == "__main__":
    main()
