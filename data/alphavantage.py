import os, json, datetime, asyncio, requests, functools
from newspaper import Article

# API_KEY = os.getenv("AV_API_KEY")
API_KEY = "31RDWIS4BVPVI89I"
TICKERS = "TSLA,NVDA,AAPL"            
LIMIT = 50

def fetch_feed(api_key: str, tickers: str, limit: int = 50000) -> list[dict]:
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers":  tickers,
        "sort":     "LATEST",
        "limit":    limit,
        "apikey":   api_key,
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    payload = r.json()

    if "feed" not in payload:            
        msg = (
            payload.get("Information")
            or payload.get("Note")
            or payload.get("Error Message")
            or str(payload)
        )
        raise RuntimeError(f"Alpha Vantage returned no feed: {msg}")
    return payload["feed"]

def iso_timestamp(ts: str) -> str:
    dt = datetime.datetime.strptime(ts, "%Y%m%dT%H%M%S")
    return dt.strftime("%Y-%m-%dT%H:%MZ")

def extract_article(url: str) -> str | None:
    try:
        art = Article(url, language="en")
        art.download()
        art.parse()
        return art.text.strip() or None
    except Exception:
        return None

async def to_entry(item: dict) -> dict:
    """
    Map one Alpha-Vantage NEWS_SENTIMENT record → your schema,
    using *only* `relevance_score` for reliability.
    """
    full_text = await asyncio.get_event_loop().run_in_executor(
        None, functools.partial(extract_article, item["url"])
    )

    # ---------- reliability purely from relevance_score -------------
    score = item.get("relevance_score")
    if score is None:                           # key missing
        reliability = "medium"                  # neutral fallback
    else:
        score = float(score)
        reliability = (
            "high"   if score >= 0.80 else
            "medium" if score >= 0.50 else
            "low"
        )

    return {
        "source":      item["source"],
        "date":        iso_timestamp(item["time_published"]),
        "reliability": reliability,
        "data":        full_text or item["title"],
    }


async def build_dataset():
    raw_feed = fetch_feed(API_KEY, TICKERS, LIMIT)

    entries = await asyncio.gather(*(to_entry(it) for it in raw_feed))

    # keep only high / medium reliability
    final = [e for e in entries if e["reliability"] in ("high", "medium")]

    with open("av_news_full.json", "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2)

    print(f"Saved {len(final)} entries (high/medium reliability) ➜ av_news_full.json")
    return final

if __name__ == "__main__":
    asyncio.run(build_dataset())
