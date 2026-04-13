import asyncio
import httpx
import json
import math
import os
import sqlite3
import time
from datetime import datetime, timezone, timedelta # Added timedelta
from typing import Optional, List, Dict, Any # Added List, Dict, Any

# ── Config ──────────────────────────────────────────────────────────────────
OPENWEATHER_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
NASA_TOKEN = os.environ.get("NASA_EARTHDATA_TOKEN", "")

# __file__ is not defined in an interactive context like Colab notebooks.
# We assume the script will run from the root of the cloned repo (/content/kv-space).
# Therefore, the database should be placed in 'krishi_veda_offline.db' relative to CWD.
CACHE_DB = os.path.join(
    os.getcwd(), "krishi_veda_offline.db"
)
SYNC_RADIUS_KM = 10.0
CACHE_TTL_HOURS = 6  # re-fetch after 6 hours

# Preferred Sentinel-2 short names for NDVI data
TARGET_NDVI_SHORT_NAMES = ["HLSS30", "HLSS30_VI", "S2_L2A-1"]

# ── Database helpers ─────────────────────────────────────────────────────────

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(os.path.abspath(CACHE_DB))
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS weather_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            radius_km REAL NOT NULL,
            fetched_at INTEGER NOT NULL,
            expires_at INTEGER NOT NULL,
            payload TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS ndvi_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            radius_km REAL NOT NULL,
            fetched_at INTEGER NOT NULL,
            expires_at INTEGER NOT NULL,
            payload TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sync_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            synced_at TEXT NOT NULL,
            sources TEXT NOT NULL,
            status TEXT NOT NULL
        );
    """
    )
    conn.commit()


# ── Cache logic ────────────────────────────────────────────────────────────

def _cache_lookup(conn: sqlite3.Connection, table_name: str, lat: float, lon: float) -> Optional[Dict[str, Any]]:
    # TODO: Also consider radius_km in lookup
    cursor = conn.execute(
        f"SELECT payload, expires_at FROM {table_name} WHERE lat=? AND lon=? ORDER BY fetched_at DESC, id DESC LIMIT 1",
        (lat, lon)
    )
    row = cursor.fetchone()
    if row and row["expires_at"] > int(time.time()):
        return json.loads(row["payload"])
    return None


def _cache_store(conn: sqlite3.Connection, table_name: str, lat: float, lon: float, payload: Dict[str, Any]) -> None:
    expires_at = int(time.time()) + CACHE_TTL_HOURS * 3600
    conn.execute(
        f"INSERT INTO {table_name} (lat, lon, radius_km, fetched_at, expires_at, payload) VALUES (?, ?, ?, ?, ?, ?)",
        (lat, lon, SYNC_RADIUS_KM, int(time.time()), expires_at, json.dumps(payload))
    )
    conn.commit()


# ── Synthetic / fallback data ──────────────────────────────────────────────

def _synthetic_weather(lat: float, lon: float) -> Dict[str, Any]:
    # Placeholder for synthetic weather data
    return {
        "temperature": 25.0, "humidity": 70, "condition": "Partly Cloudy",
        "wind_speed": 5.0, "precipitation": 0.0, "uvi": 6.0,
        "source": "Synthetic"
    }


def _synthetic_ndvi(lat: float, lon: float) -> Dict[str, Any]:
    # Placeholder for synthetic NDVI data
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "Synthetic",
        "value": 0.6,
        "image_url": "",
        "summary": "Synthetic NDVI data for demonstration."
    }


# ── Live API fetches ───────────────────────────────────────────────────────

async def _fetch_weather_live(lat: float, lon: float) -> Dict[str, Any]:
    ow_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_KEY,
        "units": "metric"
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(ow_url, params=params)
        resp.raise_for_status()
        data = resp.json()

    return {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"],
        "precipitation": data.get("rain", {}).get("1h", 0.0) + data.get("snow", {}).get("1h", 0.0),
        "uvi": data.get("uvi", 0.0),  # UVI might not always be present
        "source": "OpenWeatherMap"
    }


async def _fetch_ndvi_live(lat: float, lon: float) -> Dict[str, Any]:
    # Bounding box calculation for SYNC_RADIUS_KM
    delta_lat = SYNC_RADIUS_KM / 111.0
    delta_lon = SYNC_RADIUS_KM / (111.0 * math.cos(math.radians(lat)))

    min_lat, max_lat = lat - delta_lat, lat + delta_lat
    min_lon, max_lon = lon - delta_lon, lon + delta_lon
    bbox = f"{min_lon},{min_lat},{max_lon},{max_lat}"

    # Calculate temporal range for the last year
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=365)
    temporal_range = f"{start_date.isoformat().replace('+00:00', '')},{end_date.isoformat().replace('+00:00', '')}"

    cmr_url = "https://cmr.earthdata.nasa.gov/search/granules.json"
    headers = {
        "User-Agent": "Krishi-Veda-App/1.0",
        "Authorization": f"Bearer {NASA_TOKEN}"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        for short_name in TARGET_NDVI_SHORT_NAMES:
            params = {
                "short_name": short_name,
                "bounding_box": bbox,
                "page_size": 1,
                "sort_key": "-start_date",
                "temporal": temporal_range
            }
            try:
                resp = await client.get(cmr_url, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()

                if data["feed"]["entry"]:
                    entry = data["feed"]["entry"][0]
                    browse_url = None
                    for link in entry.get("links", []):
                        if "Browse" in link.get("rel", ""):
                            browse_url = link["href"]
                            break

                    if not browse_url:
                        print(f"⚠️ No browse image URL found for {short_name} data, but granule was found.")

                    return {
                        "timestamp": entry["time_start"],
                        "source": f"NASA_CMR_{short_name}",
                        "value": 0.5,
                        "image_url": browse_url if browse_url else "",
                        "summary": entry.get("summary", "No summary available")
                    }
            except httpx.HTTPStatusError as e:
                print(f"  Warning: HTTP Error fetching {short_name} data: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                print(f"  Warning: An error occurred fetching {short_name} data: {e}")

    raise ValueError(f"No NASA Earthdata (NDVI) found for lat={lat}, lon={lon} with any of {TARGET_NDVI_SHORT_NAMES}")


# ── Main sync function ─────────────────────────────────────────────────────

async def sync_data_for_location(lat: float, lon: float, force: bool = False) -> Dict[str, Any]:
    """
    Fetches and caches fresh data for a given location.
    If 'force' is True, bypasses cache and always fetches live.
    """
    conn = _get_conn()
    _ensure_schema(conn)

    result = {}
    sources_used = []

    # ── Weather ──
    cached_wx = None if force else _cache_lookup(conn, "weather_cache", lat, lon)
    if cached_wx:
        result["weather"] = {**cached_wx, "cache_hit": True}
        sources_used.append("weather:cache")
    else:
        if OPENWEATHER_KEY:
            try:
                wx = await _fetch_weather_live(lat, lon)
                _cache_store(conn, "weather_cache", lat, lon, wx)
                result["weather"] = {**wx, "cache_hit": False}
                sources_used.append("weather:live")
            except Exception as e:
                wx = _synthetic_weather(lat, lon)
                _cache_store(conn, "weather_cache", lat, lon, wx)
                result["weather"] = {**wx, "cache_hit": False, "error": str(e)}
                sources_used.append("weather:synthetic_fallback")
        else:
            wx = _synthetic_weather(lat, lon)
            _cache_store(conn, "weather_cache", lat, lon, wx)
            result["weather"] = {**wx, "cache_hit": False}
            sources_used.append("weather:synthetic_no_key")

    # ── NDVI / Sentinel-2 ──
    cached_ndvi = None if force else _cache_lookup(conn, "ndvi_cache", lat, lon)
    if cached_ndvi:
        result["ndvi"] = {**cached_ndvi, "cache_hit": True}
        sources_used.append("ndvi:cache")
    else:
        if NASA_TOKEN:
            try:
                ndvi = await _fetch_ndvi_live(lat, lon)
                _cache_store(conn, "ndvi_cache", lat, lon, ndvi)
                result["ndvi"] = {**ndvi, "cache_hit": False}
                sources_used.append(f"ndvi:{ndvi['source']}")
            except Exception as e:
                print(f"Error fetching live NDVI data: {e}. Falling back to synthetic.")
                ndvi = _synthetic_ndvi(lat, lon)
                _cache_store(conn, "ndvi_cache", lat, lon, ndvi)
                result["ndvi"] = {**ndvi, "cache_hit": False, "error": str(e)}
                sources_used.append("ndvi:synthetic_fallback")
        else:
            ndvi = _synthetic_ndvi(lat, lon)
            _cache_store(conn, "ndvi_cache", lat, lon, ndvi)
            result["ndvi"] = {**ndvi, "cache_hit": False}
            sources_used.append("ndvi:synthetic_no_token")


    # Log this sync
    conn.execute(
        "INSERT INTO sync_log (lat, lon, synced_at, sources, status) VALUES (?,?,?,?,?)",
        (lat, lon, datetime.now(timezone.utc).isoformat(),
         json.dumps(sources_used), "ok")
    )
    conn.commit()
    conn.close()

    result["sync_meta"] = {
        "lat": lat, "lon": lon,
        "radius_km": SYNC_RADIUS_KM,
        "sources": sources_used,
        "synced_at": datetime.now(timezone.utc).isoformat(),
    }
    return result


def get_cached(lat: float, lon: float) -> dict:
    """Synchronous cache-only lookup (no network). Used at plan time for speed."""
    conn = _get_conn()
    _ensure_schema(conn)
    wx = _cache_lookup(conn, "weather_cache", lat, lon)
    ndvi = _cache_lookup(conn, "ndvi_cache", lat, lon)
    conn.close()
    return {
        "weather": {**(wx or {}), "cache_hit": bool(wx)},
        "ndvi": {**(ndvi or {}), "cache_hit": bool(ndvi)},
    }