import json
import os
from datetime import datetime, timezone

import cache
from sources import buses, flights, weather

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def load(name):
    with open(os.path.join(FIX, name)) as f:
        return json.load(f)


def test_filter_commercial():
    rows = flights.parse_aircraft(load("aircraft.json"), 47.149, 9.521)
    kept = flights.filter_commercial(rows)
    assert [r["callsign"] for r in kept] == ["SWR123"]
    assert kept[0]["airline"] == "Swiss"


def test_filter_commercial_rules():
    low = {"callsign": "SWR1", "altitude_ft": 9000}
    cat = {"callsign": "", "category": "A5", "altitude_ft": 30000}
    private = {"callsign": "HBABC", "category": "A1", "altitude_ft": 30000}
    assert flights.filter_commercial([low, cat, private]) == [cat]


def test_unknown_airline_fallback():
    assert flights.airline_name("ZZZ123") == "Unknown airline"


def test_weather_code_mapping():
    assert "Clear" in weather.describe_weather_code(0)
    assert weather.describe_weather_code(12345) == "Unbekannt / Unknown"


def test_parse_weather():
    w = weather.parse_weather(load("weather.json"))
    assert w["temperature"] == 3.5
    assert len(w["next_hours"]) == 6
    assert w["next_hours"][0]["time"] == "13:00"


def test_minutes_until_departure():
    now = datetime(2025, 1, 15, 11, 0, tzinfo=timezone.utc)  # 12:00 +0100
    assert buses.minutes_until("2025-01-15T12:10:00+0100", now) == 10
    assert buses.minutes_until("2025-01-15T11:50:00+0100", now) == 0
    rows = buses.parse_stationboard(load("stationboard.json"), now)
    assert rows[0] == {"line": "B11", "destination": "Schaan, Bahnhof",
                       "time": "12:10", "delay": 2, "minutes": 10}


def test_cache_hits_and_expires():
    cache.clear()
    calls = []

    def fetch():
        calls.append(1)
        return "x"

    assert cache.cached("k", 60, fetch)[0] == "x"
    cache.cached("k", 60, fetch)
    assert len(calls) == 1
    cache.cached("k", 0, fetch)
    assert len(calls) == 2
