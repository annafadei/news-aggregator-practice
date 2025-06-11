from fastapi.testclient import TestClient 
from backend.app import app, news_store, store
from config import STUDENT_ID
import feedparser

client = TestClient(app)


def test_get_news_empty():
    # Перевірка порожнього стану
    news_store[STUDENT_ID] = []
    res = client.get(f"/news/{STUDENT_ID}")
    assert res.status_code == 200
    assert res.json() == {"articles": []}


def test_fetch_and_get(monkeypatch):
    # Очищення сховищ
    news_store[STUDENT_ID] = []
    store[STUDENT_ID] = []

    # Додаємо джерело через API
    response = client.post(f"/sources/{STUDENT_ID}", json={"url": "http://example.com/rss"})
    assert response.status_code == 200
    assert "http://example.com/rss" in response.json()["sources"]

    # DummyFeed з entries
    class DummyFeed:
        def __init__(self):
            self.entries = [
                {"title": "T1", "link": "http://a", "published": "2025-01-01"},
                {"title": "T2", "link": "http://b", "published": ""}
            ]

    # Підміна feedparser.parse
    monkeypatch.setattr(feedparser, "parse", lambda _: DummyFeed())

    # Запит на fetch
    res1 = client.post(f"/fetch/{STUDENT_ID}")
    assert res1.status_code == 200
    assert res1.json() == {"fetched": 2}

    # Перевірка отриманих новин
    res2 = client.get(f"/news/{STUDENT_ID}")
    assert res2.status_code == 200
    assert res2.json() == {
        "articles": [
            {"title": "T1", "link": "http://a", "published": "2025-01-01"},
            {"title": "T2", "link": "http://b", "published": ""}
        ]
    }


def test_fetch_custom_feed(monkeypatch):
    # Повне очищення
    news_store.clear()
    store.clear()
    store[STUDENT_ID] = []
    news_store[STUDENT_ID] = []

    # Додаємо користувацьке джерело
    response = client.post(f"/sources/{STUDENT_ID}", json={"url": "http://test.com/rss"})
    assert response.status_code == 200
    assert "http://test.com/rss" in response.json()["sources"]

    # DummyFeed з одним записом
    class DummyFeed:
        def __init__(self):
            self.entries = [{"title": "X", "link": "L", "published": "2025-04-28"}]

    monkeypatch.setattr(feedparser, "parse", lambda _: DummyFeed())

    # Запит на fetch
    r = client.post(f"/fetch/{STUDENT_ID}")
    assert r.status_code == 200
    assert r.json() == {"fetched": 1}