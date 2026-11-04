"""Aircraft overhead from airplanes.live (no key, max 1 request/second)."""
import math
import re

import requests

from config import REQUEST_TIMEOUT

URL = "https://api.airplanes.live/v2/point/{lat}/{lon}/{radius}"
MIN_ALTITUDE_FT = 10000

AIRLINES = {
    "SWR": "Swiss",
    "EDW": "Edelweiss Air",
    "DLH": "Lufthansa",
    "EZY": "easyJet",
    "EJU": "easyJet Europe",
    "AUA": "Austrian",
    "AFR": "Air France",
    "KLM": "KLM",
    "BAW": "British Airways",
    "RYR": "Ryanair",
    "WZZ": "Wizz Air",
    "UAE": "Emirates",
    "THY": "Turkish Airlines",
    "ETD": "Etihad",
    "QTR": "Qatar Airways",
    "IBE": "Iberia",
    "SAS": "SAS",
    "VLG": "Vueling",
    "ITY": "ITA Airways",
}

CALLSIGN_PATTERN = re.compile(r"^[A-Z]{3}\d")


def airline_name(callsign):
    """Airline name for a callsign, with a fallback for unknown codes."""
    return AIRLINES.get((callsign or "")[:3], "Unknown airline")


def distance_km(lat1, lon1, lat2, lon2):
    """Great-circle distance (haversine) in km."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(a))


def parse_aircraft(data, lat, lon):
    """Turn the raw airplanes.live JSON into a list of dicts."""
    rows = []
    for ac in data.get("ac", []):
        alt = ac.get("alt_baro")
        if not isinstance(alt, (int, float)):
            alt = None  # "ground" or missing
        callsign = (ac.get("flight") or "").strip()
        dist = None
        if ac.get("lat") is not None and ac.get("lon") is not None:
            dist = round(distance_km(lat, lon, ac["lat"], ac["lon"]), 1)
        rows.append({
            "callsign": callsign,
            "airline": airline_name(callsign),
            "registration": ac.get("r"),
            "type": ac.get("t"),
            "category": ac.get("category"),
            "altitude_ft": alt,
            "ground_speed_kt": ac.get("gs"),
            "heading": ac.get("track"),
            "lat": ac.get("lat"),
            "lon": ac.get("lon"),
            "distance_km": dist,
        })
    return rows


def filter_commercial(rows):
    """Keep airline-like flights (callsign pattern or category A3/A4/A5)
    that are above 10,000 ft."""
    result = []
    for row in rows:
        altitude = row.get("altitude_ft")
        if altitude is None or altitude <= MIN_ALTITUDE_FT:
            continue
        callsign = row.get("callsign") or ""
        looks_commercial = bool(CALLSIGN_PATTERN.match(callsign))
        if looks_commercial or row.get("category") in ("A3", "A4", "A5"):
            result.append(row)
    return result


def get_aircraft(lat, lon, radius_nm):
    """Return list of aircraft dicts, or None on any error."""
    try:
        resp = requests.get(URL.format(lat=lat, lon=lon, radius=radius_nm),
                            timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return parse_aircraft(resp.json(), lat, lon)
    except Exception:
        return None
