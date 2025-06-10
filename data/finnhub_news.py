import os, requests, datetime as dt, json, time
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv
from reliability import reliability_score

load_dotenv()
FINNHUB_TOKEN = os.getenv("FINNHUB_TOKEN") or ""
TICKERS       = ["TSLA", "NVDA", "AAPL"]
BASE_URL      = "https://finnhub.io/api/v1/company-news"
MAX_PER_CALL  = 50          # Finnhub max per request

def iso_zulu(ts_ms: int) -> str:
    return dt.datetime.utcfromtimestamp(ts_ms).strftime("%Y-%m-%dT%H:%MZ")

def classify(text: str) -> str:
    p = reliability_score(text)
    return "high" if p >= .80 else "medium" if p >= .50 else "low"

def to_entry(item: dict):
    body   = f'{item["headline"]}\n\n{item["summary"]}'.strip()
    bucket = classify(body)
    if bucket == "low":
        return None
    return {
        "source":      item["source"],
        "date":        iso_zulu(item["datetime"]),
        "reliability": bucket,
        "data":        body,
    }

def fetch_symbol(sym: str, start: dt.date, end: dt.date):
    r = requests.get(
        BASE_URL,
        params={
            "symbol": sym,
            "from":   start.isoformat(),
            "to":     end.isoformat(),
            "token":  FINNHUB_TOKEN,
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()

def month_bounds(year: int, month: int):
    first = dt.date(year, month, 1)
    next_ = (first.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    last  = next_ - dt.timedelta(days=1)
    return first, last

def grab_month(sym: str, first: dt.date, last: dt.date):
    day1 = first
    while day1 <= last:
        day7 = min(day1 + dt.timedelta(days=6), last)
        batch = fetch_symbol(sym, day1, day7)
        if not batch:
            break
        for item in batch:
            yield item
        day1 = day7 + dt.timedelta(days=1)
        time.sleep(0.35)  

def main(year: int, month: int):
    if not FINNHUB_TOKEN:
        raise SystemExit("Set FINNHUB_TOKEN in your environment.")

    first, last = month_bounds(year, month)
    print(f"Pulling {first} → {last}")

    stories, seen = defaultdict(list), set() 

    for sym in TICKERS:
        for raw in grab_month(sym, first, last):
            key = (raw["id"], raw["source"])
            if key in seen:
                continue
            seen.add(key)
            entry = to_entry(raw)
            if entry:
                stories[sym].append(entry)

    for sym, items in stories.items():
        outfile = Path(f"{sym}_news.json")
        with outfile.open("w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
        print(f"{sym}: saved {len(items)} MED/HIGH stories → {outfile}")

if __name__ == "__main__":
    now = dt.date.today()
    first_this = now.replace(day=1)
    prev_last  = first_this - dt.timedelta(days=1)
    default_y, default_m = prev_last.year, prev_last.month

    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", metavar="YYYY-MM",
                    help="month to fetch (default = previous month)")
    args = ap.parse_args()

    if args.month:
        y, m = map(int, args.month.split("-"))
    else:
        y, m = default_y, default_m

    main(y, m)