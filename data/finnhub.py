import os, requests, datetime, json

from pathlib import Path
from reliability import reliability_score 
from dotenv import load_dotenv

load_dotenv()

FINNHUB_TOKEN = os.getenv("FINNHUB_TOKEN")        
TICKERS       = ["TSLA", "NVDA", "AAPL"]          
DAYS_BACK     = 21                             
OUTFILE       = Path("finnhub_news.json")

BASE_URL = "https://finnhub.io/api/v1/company-news"


def iso(ts: int) -> str:
    """Unix-ms → ISO-8601 Zulu."""
    return datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%MZ")


def fetch_symbol(sym: str, start: str, end: str) -> list[dict]:
    """Call Finnhub company-news endpoint."""
    params = {
        "symbol": sym,
        "from":   start,
        "to":     end,
        "token":  FINNHUB_TOKEN,
    }
    r = requests.get(BASE_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()                               


def classify(body: str) -> tuple[str, float]:
    """
    Run BERT fake-news detector and bucket into high/medium/low.
    Returns (bucket, p_real)
    """
    p_real = reliability_score(body)              
    if p_real >= 0.80:
        bucket = "high"
    elif p_real >= 0.50:
        bucket = "medium"
    else:
        bucket = "low"
    return bucket, p_real


def to_entry(item: dict) -> dict | None:
    """
    Map Finnhub record → debate schema.
    Drops LOW-reliability items immediately.
    """
    body = f'{item["headline"]}\n\n{item["summary"]}'.strip()

    bucket, p = classify(body)
    if bucket == "low":           
        return None

    return {
        "source":      item["source"],
        "date":        iso(item["datetime"]),
        "reliability": bucket,   
        "data":        body
    }


def main() -> None:
    end   = datetime.date.today()
    start = end - datetime.timedelta(days=DAYS_BACK)
    frm, to = start.isoformat(), end.isoformat()

    master, seen = [], set()
    for sym in TICKERS:
        for raw in fetch_symbol(sym, frm, to):
            if raw["id"] in seen:
                continue
            seen.add(raw["id"])
            entry = to_entry(raw)
            if entry:
                master.append(entry)

    OUTFILE.write_text(json.dumps(master, indent=2))
    print(f"Saved {len(master)} MED/HIGH stories → {OUTFILE}")


if __name__ == "__main__":
    if not FINNHUB_TOKEN:
        raise SystemExit("Set FINNHUB_TOKEN env var first.")
    main()

