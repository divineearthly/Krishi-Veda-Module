"""
Offline Sovereign Sync Manager
================================
Fetches NASA Sentinel-2 NDVI and OpenWeather data for a 10 km radius
around a GPS coordinate and caches it into a local SQLite file.

Run once to prime the cache; the /api/v1/plan endpoint then works fully
offline from the cached data.
"""
import asyncio
import httpx
import json
import math
import os
import sqlite3
import time
from datetime import datetime, timezone
from typing import Optional

# ── Config ──────────────────────────────────────────────────────────────────
OPENWEATHER_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
NASA_TOKEN = os.environ.get("NASA_EARTHDATA_TOKEN", "")

CACHE_DB = os.path.join(
    os.path.dirname(__file__), "../../krishi_veda_offline.db"
)
SYNC_RADIUS_KM = 10.0
CACHE_TTL_HOURS = 6  # re-fetch after 6 hours


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
            lat REAL,
            lon REAL,
            synced_at TEXT,
            sources TEXT,
            status TEXT
        );
    """)
    conn.commit()


def _bbox(lat: float, lon: float, km: float):
    """Return (min_lat, min_lon, max_lat, max_lon) for a square km-radius bbox."""
    deg_lat = km / 111.0
    deg_lon = km / (111.0 * math.cos(math.radians(lat)))
    return lat - deg_lat, lon - deg_lon, lat + deg_lat, lon + deg_lon


def _cache_lookup(conn: sqlite3.Connection, table: str, lat: float, lon: float) -> Optional[dict]:
    now = int(time.time())
    row = conn.execute(
        f"SELECT payload, expires_at FROM {table} "
        "WHERE ABS(lat-?) < 0.09 AND ABS(lon-?) < 0.09 AND expires_at > ? "
        "ORDER BY fetched_at DESC LIMIT 1",
        (lat, lon, now)
    ).fetchone()
    if row:
        return json.loads(row["payload"])
    return None


def _cache_store(conn: sqlite3.Connection, table: str,
                  lat: float, lon: float, payload: dict) -> None:
    now = int(time.time())
    expires = now + CACHE_TTL_HOURS * 3600
    conn.execute(
        f"INSERT INTO {table} (lat, lon, radius_km, fetched_at, expires_at, payload) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (lat, lon, SYNC_RADIUS_KM, now, expires, json.dumps(payload))
    )
    conn.commit()


# ── OpenWeather Sync ─────────────────────────────────────────────────────────

async def _fetch_openweather_live(lat: float, lon: float) -> dict:
    """Fetch current weather + 5-day forecast from OpenWeather."""
    async with httpx.AsyncClient(timeout=8.0) as client:
        current = await client.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"lat": lat, "lon": lon, "appid": OPENWEATHER_KEY, "units": "metric"}
        )
        current.raise_for_status()
        forecast = await client.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={"lat": lat, "lon": lon, "appid": OPENWEATHER_KEY,
                    "units": "metric", "cnt": 40}
        )
        forecast.raise_for_status()
        cd = current.json()
        fd = forecast.json()

        daily = {}
        for item in fd.get("list", []):
            date = item["dt_txt"][:10]
            daily.setdefault(date, []).append(item["main"]["temp"])

        forecast_days = {
            d: {"avg_temp": round(sum(v)/len(v), 1), "count": len(v)}
            for d, v in list(daily.items())[:5]
        }

        return {
            "source": "openweather_live",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "location": cd.get("name", ""),
            "temperature_c": cd["main"]["temp"],
            "feels_like_c": cd["main"]["feels_like"],
            "humidity_pct": cd["main"]["humidity"],
            "pressure_hpa": cd["main"]["pressure"],
            "wind_speed_ms": cd["wind"]["speed"],
            "rainfall_mm_monthly": cd.get("rain", {}).get("1h", 0) * 720,
            "description": cd["weather"][0]["description"],
            "season": _infer_season(lat),
            "forecast_5day": forecast_days,
            "radius_km": SYNC_RADIUS_KM,
        }


def _infer_season(lat: float) -> str:
    m = datetime.utcnow().month
    if 6 <= m <= 9:
        return "monsoon"
    if 10 <= m <= 11:
        return "post_monsoon"
    if m <= 2 or m == 12:
        return "winter"
    return "summer"


def _synthetic_weather(lat: float, lon: float) -> dict:
    m = datetime.utcnow().month
    season = _infer_season(lat)
    rain = 150 if season == "monsoon" else 40 if season == "post_monsoon" else 8
    temp = 28 if season == "monsoon" else 24 if season == "post_monsoon" else (15 + lat*-0.4) if season == "winter" else 32
    return {
        "source": "synthetic_offline",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "temperature_c": round(temp, 1),
        "humidity_pct": 65 if season == "monsoon" else 45,
        "rainfall_mm_monthly": round(rain, 1),
        "season": season,
        "radius_km": SYNC_RADIUS_KM,
    }


# ── NASA Sentinel-2 / NDVI Sync ──────────────────────────────────────────────

async def _fetch_ndvi_live(lat: float, lon: float) -> dict:
    """
    Query NASA Earth Search (AWS STAC) for recent Sentinel-2 L2A scenes
    and compute a synthetic NDVI from scene statistics.
    """
    min_lat, min_lon, max_lat, max_lon = _bbox(lat, lon, SYNC_RADIUS_KM)
    bbox = [min_lon, min_lat, max_lon, max_lat]

    stac_url = "https://earth-search.aws.element84.com/v1/search"
    # Rolling 180-day window for recent imagery
    from datetime import timedelta
    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(days=180)
    dt_range = f"{start_dt.strftime('%Y-%m-%d')}/{end_dt.strftime('%Y-%m-%d')}"
    payload = {
        "collections": ["sentinel-2-l2a"],
        "bbox": bbox,
        "datetime": dt_range,
        "limit": 3,
        "fields": {
            "include": ["properties.datetime", "properties.eo:cloud_cover",
                        "properties.s2:vegetation_percentage",
                        "properties.s2:water_percentage"],
            "exclude": ["assets", "links"]
        }
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(stac_url, json=payload)
        resp.raise_for_status()
        data = resp.json()

    features = data.get("features", [])
    if not features:
        return _synthetic_ndvi(lat, lon)

    # Average vegetation % across available scenes
    veg_pcts = [
        f["properties"].get("s2:vegetation_percentage", 0)
        for f in features
        if f["properties"].get("s2:vegetation_percentage") is not None
    ]
    avg_veg = sum(veg_pcts) / len(veg_pcts) if veg_pcts else 30.0
    ndvi = round(0.1 + avg_veg / 130.0, 3)
    ndvi = min(0.9, max(0.05, ndvi))

    return {
        "source": "nasa_sentinel2_stac",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "scene_count": len(features),
        "avg_vegetation_pct": round(avg_veg, 1),
        "ndvi": ndvi,
        "evi": round(ndvi * 0.85, 3),
        "crop_health": "Good" if ndvi > 0.5 else "Moderate" if ndvi > 0.3 else "Poor",
        "bbox_10km": bbox,
        "radius_km": SYNC_RADIUS_KM,
    }


def _synthetic_ndvi(lat: float, lon: float) -> dict:
    m = datetime.utcnow().month
    geo = max(0, 1 - abs(lat - 23) / 20) * max(0, 1 - abs(lon - 82) / 30)
    season_f = 0.7 if 7 <= m <= 10 else 0.4
    ndvi = round(min(0.9, 0.2 + geo * 0.5 * season_f + 0.1), 3)
    return {
        "source": "synthetic_offline",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "ndvi": ndvi,
        "evi": round(ndvi * 0.85, 3),
        "crop_health": "Good" if ndvi > 0.5 else "Moderate" if ndvi > 0.3 else "Poor",
        "radius_km": SYNC_RADIUS_KM,
    }


# ── Main Sync Entry Point ────────────────────────────────────────────────────

async def sync_location(lat: float, lon: float, force: bool = False) -> dict:
    """
    Sync data for a 10km radius around (lat, lon).
    Checks cache first; fetches live only if expired or force=True.
    Returns a dict with 'weather' and 'ndvi' keys.
    """
    conn = _get_conn()
    _ensure_schema(conn)

    sources_used = []
    result = {}

    # ── Weather ──
    cached_wx = None if force else _cache_lookup(conn, "weather_cache", lat, lon)
    if cached_wx:
        result["weather"] = {**cached_wx, "cache_hit": True}
        sources_used.append("weather:cache")
    else:
        if OPENWEATHER_KEY:
            try:
                wx = await _fetch_openweather_live(lat, lon)
                _cache_store(conn, "weather_cache", lat, lon, wx)
                result["weather"] = {**wx, "cache_hit": False}
                sources_used.append("weather:openweather_live")
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
        try:
            ndvi = await _fetch_ndvi_live(lat, lon)
            _cache_store(conn, "ndvi_cache", lat, lon, ndvi)
            result["ndvi"] = {**ndvi, "cache_hit": False}
            sources_used.append(f"ndvi:{ndvi['source']}")
        except Exception as e:
            ndvi = _synthetic_ndvi(lat, lon)
            _cache_store(conn, "ndvi_cache", lat, lon, ndvi)
            result["ndvi"] = {**ndvi, "cache_hit": False, "error": str(e)}
            sources_used.append("ndvi:synthetic_fallback")

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
