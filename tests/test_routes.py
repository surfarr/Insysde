import json
import os

import pytest

import app as dash
import cache
from sources import buses, flights, weather

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def load(name):
    with open(os.path.join(FIX, name)) as f:
        return json.load(f)


@pytest.fixture
def client():
    cache.clear()
    dash.app.config["TESTING"] = True
    return dash.app.test_client()


@pytest.fixture
def sample(monkeypatch):
    monkeypatch.setattr(dash.weather, "get_weather",
                        lambda lat, lon: weather.parse_weather(load("weather.json")))
    monkeypatch.setattr(dash.buses, "get_departures",
                        lambda name, limit=8: buses.parse_stationboard(load("stationboard.json")))
    monkeypatch.setattr(dash.flights, "get_aircraft",
                        lambda lat, lon, r: flights.parse_aircraft(load("aircraft.json"), lat, lon))


@pytest.fixture
def broken(monkeypatch):
    monkeypatch.setattr(dash.weather, "get_weather", lambda lat, lon: None)
    monkeypatch.setattr(dash.buses, "get_departures", lambda name, limit=8: None)
    monkeypatch.setattr(dash.flights, "get_aircraft", lambda lat, lon, r: None)


PAGES = ["/", "/weather", "/buses", "/flights", "/about"]


@pytest.mark.parametrize("url", PAGES)
def test_pages_with_data(client, sample, url):
    assert client.get(url).status_code == 200


def test_dashboard_content(client, sample):
    html = client.get("/").get_data(as_text=True)
    assert "SWR123" in html and "Schaan, Bahnhof" in html
    assert 'http-equiv="refresh"' in html


@pytest.mark.parametrize("url", PAGES)
def test_pages_when_sources_fail(client, broken, url):
    r = client.get(url)
    assert r.status_code == 200
    if url != "/about":
        assert "currently unavailable" in r.get_data(as_text=True)


def test_partial_failure_still_renders(client, sample, monkeypatch):
    monkeypatch.setattr(dash.buses, "get_departures", lambda name, limit=8: None)
    html = client.get("/").get_data(as_text=True)
    assert "currently unavailable" in html and "SWR123" in html


def test_api_summary(client, sample):
    data = client.get("/api/summary").get_json()
    assert set(data) == {"weather", "buses", "flights"}
    assert data["buses"]["data"][0]["line"] == "B11"


def test_api_summary_none(client, broken):
    assert client.get("/api/summary").get_json()["weather"]["data"] is None


def test_404(client):
    assert client.get("/nope").status_code == 404
