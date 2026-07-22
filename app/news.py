import datetime
import html
import re
import time

import httpx
from defusedxml import ElementTree as SafeET

from app.config import settings

# Hardcoded allowlist - no user-supplied feed URLs are ever accepted, so this module
# can't be pointed at arbitrary/untrusted hosts.
FEEDS: list[tuple[str, str]] = [
    ("MarketWatch", "https://feeds.content.dowjones.io/public/rss/mw_topstories"),
    ("MarketWatch Market Pulse", "https://feeds.content.dowjones.io/public/rss/mw_marketpulse"),
    ("CNBC Markets", "https://www.cnbc.com/id/20910258/device/rss/rss.html"),
]

CACHE_TTL_SECONDS = 15 * 60
_TAG_RE = re.compile(r"<[^>]+>")

_cache: dict = {"headlines": [], "trend_summary": None, "fetched_at": 0.0}


def _clean_text(raw: str | None) -> str:
    if not raw:
        return ""
    return html.unescape(_TAG_RE.sub("", raw)).strip()


def _parse_rss(xml_text: str, source: str) -> list[dict]:
    """Parses RSS 2.0 XML using a hardened parser (no external entity resolution),
    so a malformed or malicious feed response can't do more than fail to parse."""
    root = SafeET.fromstring(xml_text)
    items = []
    for item in root.iter("item"):
        title = _clean_text((item.findtext("title") or "").strip())
        link = (item.findtext("link") or "").strip()
        if not title or not link:
            continue
        pub_date = (item.findtext("pubDate") or "").strip()
        items.append(
            {
                "title": title,
                "link": link,
                "source": source,
                "summary": _clean_text(item.findtext("description")),
                "published": pub_date,
            }
        )
    return items


def _fetch_feed(source: str, url: str) -> list[dict]:
    try:
        response = httpx.get(url, timeout=8.0, headers={"User-Agent": "personal-finance-bot/1.0"})
        response.raise_for_status()
        return _parse_rss(response.text, source)
    except Exception:
        return []  # one dead/slow feed shouldn't break the whole panel


def fetch_all_headlines(limit_per_feed: int = 8) -> list[dict]:
    headlines = []
    for source, url in FEEDS:
        headlines.extend(_fetch_feed(source, url)[:limit_per_feed])
    return headlines


TREND_SUMMARY_SYSTEM_PROMPT = """You summarize financial news headlines into a short, neutral overview \
of what's happening in the markets right now (stocks, bonds, ETFs, rates, notable sector moves).

Strict rules:
- Describe trends and events only. Never recommend buying, selling, or holding anything.
- Never give personal financial advice or tell the reader what they should do.
- If headlines are mixed/contradictory, say so rather than picking a side.
- 3-5 sentences, plain language, no bullet points.
"""


def summarize_trends(headlines: list[dict]) -> str | None:
    """Isolated, tool-less call: this model invocation has no access to the user's tools/data,
    only the public headlines below - so even a headline crafted to inject instructions has
    nothing to act on."""
    if not settings.anthropic_api_key or not headlines:
        return None
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    headline_text = "\n".join(f"- [{h['source']}] {h['title']}" for h in headlines)
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=300,
        system=TREND_SUMMARY_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": headline_text}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def get_news(force_refresh: bool = False) -> dict:
    stale = (time.time() - _cache["fetched_at"]) > CACHE_TTL_SECONDS
    if force_refresh or stale or not _cache["headlines"]:
        headlines = fetch_all_headlines()
        if headlines:  # keep serving the old cache if every feed failed this round
            _cache["headlines"] = headlines
            _cache["trend_summary"] = summarize_trends(headlines)
            _cache["fetched_at"] = time.time()

    return {
        "headlines": _cache["headlines"],
        "trend_summary": _cache["trend_summary"],
        "updated_at": datetime.datetime.fromtimestamp(_cache["fetched_at"], tz=datetime.timezone.utc).isoformat()
        if _cache["fetched_at"]
        else None,
    }
