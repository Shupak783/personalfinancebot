import time

import pytest

from app import news as news_module
from app.news import _parse_rss, fetch_all_headlines, get_news, summarize_trends

SAMPLE_RSS = """<?xml version="1.0"?>
<rss version="2.0"><channel>
<title>Test Feed</title>
<item>
  <title>Stocks rally on Fed news</title>
  <link>https://example.com/a</link>
  <description>&lt;p&gt;Stocks rose &amp; bonds fell today.&lt;/p&gt;</description>
  <pubDate>Mon, 01 Jan 2026 12:00:00 GMT</pubDate>
</item>
<item>
  <title>ETF trends to watch</title>
  <link>https://example.com/b</link>
  <description>Investors eye new ETFs.</description>
</item>
</channel></rss>"""

MALICIOUS_XML = """<?xml version="1.0"?>
<!DOCTYPE rss [<!ENTITY xxe "pwned">]>
<rss><channel><item><title>&xxe;</title><link>http://example.com</link></item></channel></rss>"""


@pytest.fixture(autouse=True)
def reset_cache():
    news_module._cache["headlines"] = []
    news_module._cache["trend_summary"] = None
    news_module._cache["fetched_at"] = 0.0
    yield
    news_module._cache["headlines"] = []
    news_module._cache["trend_summary"] = None
    news_module._cache["fetched_at"] = 0.0


def test_parse_rss_extracts_items_and_cleans_html():
    items = _parse_rss(SAMPLE_RSS, "TestSource")
    assert len(items) == 2
    assert items[0]["title"] == "Stocks rally on Fed news"
    assert items[0]["source"] == "TestSource"
    assert items[0]["summary"] == "Stocks rose & bonds fell today."  # tags stripped, entities unescaped
    assert items[1]["link"] == "https://example.com/b"


def test_parse_rss_skips_items_missing_title_or_link():
    xml = "<rss><channel><item><title>No link here</title></item></channel></rss>"
    assert _parse_rss(xml, "Test") == []


def test_parse_rss_rejects_entity_declarations():
    """Guards the XXE/entity-expansion claim made to the user: a feed can't smuggle
    instructions/content through XML entities, defusedxml refuses to parse it at all."""
    with pytest.raises(Exception):
        _parse_rss(MALICIOUS_XML, "Malicious")


def test_fetch_all_headlines_skips_a_failing_feed(monkeypatch):
    def fake_get(url, timeout=8.0, headers=None):
        if "marketpulse" in url:
            raise ConnectionError("feed is down")

        class FakeResponse:
            text = SAMPLE_RSS

            def raise_for_status(self):
                pass

        return FakeResponse()

    monkeypatch.setattr(news_module.httpx, "get", fake_get)
    headlines = fetch_all_headlines()
    assert len(headlines) == 4  # 2 items x 2 of the 3 feeds; the failing one contributes nothing


def test_summarize_trends_returns_none_without_api_key(monkeypatch):
    monkeypatch.setattr(news_module.settings, "anthropic_api_key", "")
    assert summarize_trends([{"source": "x", "title": "y"}]) is None


def test_summarize_trends_never_gets_tool_access(monkeypatch):
    monkeypatch.setattr(news_module.settings, "anthropic_api_key", "fake-key")
    captured = {}

    class FakeBlock:
        type = "text"
        text = "Markets were mixed today across sectors."

    class FakeResponse:
        content = [FakeBlock()]

    class FakeMessages:
        def create(self, **kwargs):
            captured.update(kwargs)
            return FakeResponse()

    class FakeClient:
        def __init__(self, api_key):
            self.messages = FakeMessages()

    import anthropic

    monkeypatch.setattr(anthropic, "Anthropic", FakeClient)

    result = summarize_trends([{"source": "CNBC", "title": "Stocks rise"}])

    assert result == "Markets were mixed today across sectors."
    assert "tools" not in captured  # isolated call: literally cannot invoke any tool
    assert "never recommend" in captured["system"].lower()


def test_get_news_uses_cache_when_fresh(monkeypatch):
    news_module._cache["headlines"] = [{"title": "cached", "link": "x", "source": "s", "summary": "", "published": ""}]
    news_module._cache["trend_summary"] = "cached summary"
    news_module._cache["fetched_at"] = time.time()

    called = {"count": 0}

    def fake_fetch_all(limit_per_feed=8):
        called["count"] += 1
        return []

    monkeypatch.setattr(news_module, "fetch_all_headlines", fake_fetch_all)

    result = get_news()
    assert called["count"] == 0
    assert result["headlines"][0]["title"] == "cached"


def test_get_news_refreshes_when_stale(monkeypatch):
    news_module._cache["headlines"] = [{"title": "old", "link": "x", "source": "s", "summary": "", "published": ""}]
    news_module._cache["fetched_at"] = time.time() - news_module.CACHE_TTL_SECONDS - 1

    monkeypatch.setattr(news_module, "fetch_all_headlines", lambda limit_per_feed=8: [
        {"title": "fresh", "link": "y", "source": "s", "summary": "", "published": ""}
    ])
    monkeypatch.setattr(news_module, "summarize_trends", lambda headlines: "fresh summary")

    result = get_news()
    assert result["headlines"][0]["title"] == "fresh"
    assert result["trend_summary"] == "fresh summary"
