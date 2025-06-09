import yfinance as yf, pandas as pd, datetime
start = "2025-05-01"; end = "2025-05-31"
df = yf.download("TSLA NVDA AAPL", start=start, end=end, group_by="ticker")

rows = []
for sym in ["TSLA","NVDA","AAPL"]:
    for idx, row in df[sym].iterrows():
        rows.append({
            "date":   idx.strftime("%Y-%m-%d"),
            "symbol": sym,
            "open":   row["Open"],
            "high":   row["High"],
            "low":    row["Low"],
            "close":  row["Close"],
            "volume": int(row["Volume"]),
        })
pd.DataFrame(rows).to_csv("prices.csv", index=False)
