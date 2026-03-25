/**
 * Krishi-Veda IndexedDB Module
 * Stores offline sync data: weather forecasts and NASA NDVI stats.
 * Exposes a simple promise-based API used by the sync button and plan loader.
 */

const IDB_NAME    = 'krishiVedaDB';
const IDB_VERSION = 2;

const STORE_WEATHER = 'last_synced_weather';   // keyed by "lat_lon"
const STORE_NDVI    = 'nasa_ndvi_stats';        // keyed by "lat_lon"
const STORE_META    = 'sync_meta';              // last sync timestamps

let _db = null;

// ── Open / upgrade ──────────────────────────────────────────────────────────
function openDB() {
  if (_db) return Promise.resolve(_db);

  return new Promise((resolve, reject) => {
    const req = indexedDB.open(IDB_NAME, IDB_VERSION);

    req.onupgradeneeded = (e) => {
      const db = e.target.result;

      if (!db.objectStoreNames.contains(STORE_WEATHER)) {
        db.createObjectStore(STORE_WEATHER, { keyPath: 'location_key' });
      }
      if (!db.objectStoreNames.contains(STORE_NDVI)) {
        db.createObjectStore(STORE_NDVI, { keyPath: 'location_key' });
      }
      if (!db.objectStoreNames.contains(STORE_META)) {
        db.createObjectStore(STORE_META, { keyPath: 'id' });
      }
    };

    req.onsuccess = (e) => { _db = e.target.result; resolve(_db); };
    req.onerror   = (e) => reject(e.target.error);
  });
}

function locationKey(lat, lon) {
  return `${parseFloat(lat).toFixed(3)}_${parseFloat(lon).toFixed(3)}`;
}

// ── Generic helpers ──────────────────────────────────────────────────────────
async function idbPut(storeName, record) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx  = db.transaction(storeName, 'readwrite');
    const req = tx.objectStore(storeName).put(record);
    req.onsuccess = () => resolve(req.result);
    req.onerror   = (e) => reject(e.target.error);
  });
}

async function idbGet(storeName, key) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx  = db.transaction(storeName, 'readonly');
    const req = tx.objectStore(storeName).get(key);
    req.onsuccess = () => resolve(req.result || null);
    req.onerror   = (e) => reject(e.target.error);
  });
}

// ── Public API ───────────────────────────────────────────────────────────────

/**
 * Save weather data (including 7-day forecast) for a location.
 * @param {number} lat
 * @param {number} lon
 * @param {object} weatherData  — the full API response
 */
async function saveWeather(lat, lon, weatherData) {
  const key = locationKey(lat, lon);
  await idbPut(STORE_WEATHER, {
    location_key: key,
    lat, lon,
    synced_at: Date.now(),
    data: weatherData,
  });
  await idbPut(STORE_META, {
    id: 'last_weather_sync',
    lat, lon, key,
    synced_at: Date.now(),
    source: weatherData.source || 'unknown',
  });
}

/**
 * Save NASA NDVI data for a location.
 */
async function saveNdvi(lat, lon, ndviData) {
  const key = locationKey(lat, lon);
  await idbPut(STORE_NDVI, {
    location_key: key,
    lat, lon,
    synced_at: Date.now(),
    data: ndviData,
  });
  await idbPut(STORE_META, {
    id: 'last_ndvi_sync',
    lat, lon, key,
    synced_at: Date.now(),
    source: ndviData.source || 'unknown',
  });
}

/**
 * Retrieve cached weather for a location (returns null if not cached).
 */
async function getWeather(lat, lon) {
  const key = locationKey(lat, lon);
  const record = await idbGet(STORE_WEATHER, key);
  return record ? record.data : null;
}

/**
 * Retrieve cached NDVI for a location (returns null if not cached).
 */
async function getNdvi(lat, lon) {
  const key = locationKey(lat, lon);
  const record = await idbGet(STORE_NDVI, key);
  return record ? record.data : null;
}

/**
 * Return metadata about the last sync (timestamp, source, location).
 */
async function getLastSyncMeta() {
  const weather = await idbGet(STORE_META, 'last_weather_sync');
  const ndvi    = await idbGet(STORE_META, 'last_ndvi_sync');
  return { weather, ndvi };
}

/**
 * Human-readable age of the last sync, e.g. "2h 15m ago" or "Never".
 */
async function syncAgeLabel() {
  const meta = await getLastSyncMeta();
  const ts   = meta.weather?.synced_at || meta.ndvi?.synced_at;
  if (!ts) return 'Never synced';
  const diffMs  = Date.now() - ts;
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1)   return 'Just now';
  if (diffMin < 60)  return `${diffMin}m ago`;
  const h = Math.floor(diffMin / 60);
  const m = diffMin % 60;
  return m > 0 ? `${h}h ${m}m ago` : `${h}h ago`;
}

// Export for use in inline scripts
window.KrishiIDB = { saveWeather, saveNdvi, getWeather, getNdvi, getLastSyncMeta, syncAgeLabel };
