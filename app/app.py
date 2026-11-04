"""Campus Dashboard - routes only. Logic lives in cache.py and sources/."""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, render_template  # noqa: E402

import config  # noqa: E402
from cache import cached  # noqa: E402
from sources import buses, flights, weather  # noqa: E402

app = Flask(__name__)


def stamp(ts):
    return datetime.fromtimestamp(ts).strftime("%H:%M:%S")


def load_weather():
    value, ts = cached("weather", config.CACHE_SECONDS,
                       lambda: weather.get_weather(config.CAMPUS_LAT, config.CAMPUS_LON))
    return {"data": value, "updated": stamp(ts)}


def load_buses():
    value, ts = cached("buses", config.CACHE_SECONDS,
                       lambda: buses.get_departures(config.BUS_STATION_NAME))
    return {"data": value, "updated": stamp(ts)}


def load_flights():
    def fetch():
        rows = flights.get_aircraft(config.CAMPUS_LAT, config.CAMPUS_LON,
                                    config.FLIGHT_RADIUS_NM)
        return None if rows is None else flights.filter_commercial(rows)

    value, ts = cached("flights", config.CACHE_SECONDS, fetch)
    return {"data": value, "updated": stamp(ts)}


@app.route("/")
def dashboard():
    return render_template("dashboard.html", weather=load_weather(),
                           buses=load_buses(), flights=load_flights(),
                           refresh=config.CACHE_SECONDS)


@app.route("/weather")
def weather_page():
    return render_template("weather.html", weather=load_weather())


@app.route("/buses")
def buses_page():
    return render_template("buses.html", buses=load_buses(),
                           station=config.BUS_STATION_NAME)


@app.route("/flights")
def flights_page():
    return render_template("flights.html", flights=load_flights(),
                           radius=config.FLIGHT_RADIUS_NM)


@app.route("/api/summary")
def summary():
    return jsonify({
        "weather": load_weather(),
        "buses": load_buses(),
        "flights": load_flights(),
    })


@app.route("/about")
def about():
    return render_template("about.html")


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
