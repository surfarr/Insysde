"""Bus departures from transport.opendata.ch."""
from datetime import datetime, timezone

import requests

from config import REQUEST_TIMEOUT

BASE = "https://transport.opendata.ch/v1"


def minutes_until(departure_iso, now=None):
    """Whole minutes from `now` until an ISO timestamp (never below 0)."""
    dep = datetime.strptime(departure_iso, "%Y-%m-%dT%H:%M:%S%z")
    if now is None:
        now = datetime.now(timezone.utc)
    return max(0, int((dep - now).total_seconds() // 60))


def parse_stationboard(data, now=None):
    """Turn the raw stationboard JSON into a list of dicts."""
    rows = []
    for item in data["stationboard"]:
        stop = item["stop"]
        rows.append({
            "line": (item.get("category") or "") + (item.get("number") or ""),
            "destination": item.get("to"),
            "time": stop["departure"][11:16],
            "delay": stop.get("delay"),
            "minutes": minutes_until(stop["departure"], now),
        })
    return rows


def get_departures(station_name, limit=8):
    """Return a list of departure dicts, or None on any error."""
    try:
        r = requests.get(BASE + "/locations", params={"query": station_name},
                         timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        station_id = r.json()["stations"][0]["id"]
        r = requests.get(BASE + "/stationboard",
                         params={"id": station_id, "limit": limit},
                         timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return parse_stationboard(r.json())
    except Exception:
        return None
