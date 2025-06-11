from fastapi.testclient import TestClient
from backend.app import app, news_store, store
from config import STUDENT_ID
import feedparser

client = TestClient(app)

# Dummy клас для підміни feedparser.parse
class DummyFeed:
    def __init__(self):
        self.entries = [
            {"title": "T1", "link": "http://a", "published": "2025-01-01"},
            {"title": "T2", "link": "http://b", "published": ""}
        ]

def test_get_news_empty():
    # Порожній початковий стан
    news_store[STUDENT_ID] = []
    res = client.get(f"/news/{STUDENT_ID}")
    assert res.status_code == 200
    assert res.json() == {"articles": []}

def test_fetch_and_get(monkeypatch):
    # Підміна джерела у config.SOURCES
    monkeypatch.setattr("config.SOURCES", ["http://example.com/rss"])
    monkeypatch.setattr(feedparser, "parse", lambda url: DummyFeed())

    news_store[STUDENT_ID] = []
    res1 = client.post(f"/fetch/{STUDENT_ID}")
    assert res1.status_code == 200
    assert res1.json() == {"fetched": 2}

    res2 = client.get(f"/news/{STUDENT_ID}")
    assert res2.status_code == 200
    assert res2.json() == {
        "articles": [
            {"title": "T1", "link": "http://a", "published": "2025-01-01"},
            {"title": "T2", "link": "http://b", "published": ""}
        ]
    }

def test_fetch_custom_feed(monkeypatch):
    # Очищення сховищ
    news_store.clear()
    store.clear()
    store[STUDENT_ID] = []
    news_store[STUDENT_ID] = []

    # Додаємо кастомне джерело
    response = client.post(f"/sources/{STUDENT_ID}", json={"url": "http://test.com/rss"})
    assert response.status_code == 200
    assert "http://test.com/rss" in response.json()["sources"]

    # Створення окремого DummyFeed
    class DummySingleFeed:
        entries = [{"title": "X", "link": "L", "published": "2025-04-28"}]

    # Підміна парсера
    monkeypatch.setattr(feedparser, "parse", lambda _: DummySingleFeed())

    # Fetch і перевірка
    r = client.post(f"/fetch/{STUDENT_ID}")
    assert r.status_code == 200
    assert r.json() == {"fetched": 1}