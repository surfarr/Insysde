"""A very simple in-memory cache: key -> (timestamp, value)."""
import time

_store = {}


def cached(key, seconds, fetch_function):
    """Return the cached value for key if younger than `seconds`, else fetch.

    Returns a (value, fetched_at) tuple so pages can show "last updated".
    None results are cached too, so a failing API is not hammered.
    """
    now = time.time()
    if key in _store:
        timestamp, value = _store[key]
        if now - timestamp < seconds:
            return value, timestamp
    value = fetch_function()
    _store[key] = (now, value)
    return value, now


def clear():
    _store.clear()
