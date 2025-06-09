from functools import lru_cache
from transformers import pipeline

@lru_cache(maxsize=1)
def _load_detector():
    return pipeline(
        "text-classification",
        model="jy46604790/Fake-News-Bert-Detect",   
        truncation=True,
        max_length=512,
        top_k=1,
    )

def reliability_score(text: str) -> float:
    """
    Returns P(real_news) in [0, 1].
    Falls back to 0.5 if the model crashes.
    """
    try:
        out = _load_detector()(text[:512])[0]
        label, prob = out["label"].upper(), out["score"]
        return prob if label in ("REAL", "REAL_NEWS", "TRUE") else 1 - prob
    except Exception:
        return 0.5
