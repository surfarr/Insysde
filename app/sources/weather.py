"""Weather from Open-Meteo (no API key)."""
import requests

from config import REQUEST_TIMEOUT

URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "Klar / Clear",
    1: "Überwiegend klar / Mostly clear",
    2: "Teilweise bewölkt / Partly cloudy",
    3: "Bedeckt / Overcast",
    45: "Nebel / Fog",
    48: "Reifnebel / Rime fog",
    51: "Leichter Nieselregen / Light drizzle",
    53: "Nieselregen / Drizzle",
    55: "Starker Nieselregen / Heavy drizzle",
    61: "Leichter Regen / Light rain",
    63: "Regen / Rain",
    65: "Starker Regen / Heavy rain",
    71: "Leichter Schneefall / Light snow",
    73: "Schneefall / Snow",
    75: "Starker Schneefall / Heavy snow",
    80: "Regenschauer / Rain showers",
    81: "Starke Regenschauer / Heavy showers",
    82: "Heftige Regenschauer / Violent showers",
    95: "Gewitter / Thunderstorm",
    96: "Gewitter mit Hagel / Thunderstorm with hail",
    99: "Starkes Gewitter mit Hagel / Severe thunderstorm with hail",
}


def describe_weather_code(code):
    """Map a WMO weather code to a short description."""
    return WEATHER_CODES.get(code, "Unbekannt / Unknown")


def parse_weather(data, hours=6):
    """Turn the raw Open-Meteo JSON into a simple dict."""
    cur = data["current"]
    hourly = data["hourly"]
    # Start at the first hour that is not before the current time.
    start = 0
    for i, t in enumerate(hourly["time"]):
        if t >= cur["time"][:13] + ":00":
            start = i
            break
    forecast = []
    for i in range(start + 1, min(start + 1 + hours, len(hourly["time"]))):
        forecast.append({
            "time": hourly["time"][i][11:16],
            "temperature": hourly["temperature_2m"][i],
            "precipitation": hourly["precipitation"][i],
            "description": describe_weather_code(hourly["weather_code"][i]),
        })
    return {
        "temperature": cur["temperature_2m"],
        "apparent_temperature": cur["apparent_temperature"],
        "wind_speed": cur["wind_speed_10m"],
        "precipitation": cur["precipitation"],
        "weather_code": cur["weather_code"],
        "description": describe_weather_code(cur["weather_code"]),
        "next_hours": forecast,
    }


def get_weather(lat, lon):
    """Return weather dict, or None on any error."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,apparent_temperature,wind_speed_10m,"
                   "precipitation,weather_code",
        "hourly": "temperature_2m,precipitation,weather_code",
        "forecast_hours": 8,
        "timezone": "Europe/Zurich",
    }
    try:
        resp = requests.get(URL, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return parse_weather(resp.json())
    except Exception:
        return None
