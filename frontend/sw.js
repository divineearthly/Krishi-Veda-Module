/**
 * Krishi-Veda Service Worker — Cache-First Strategy
 * Caches all frontend assets so the app works fully offline after first load.
 */

const CACHE_VERSION = 'krishi-veda-v3';

// All assets to pre-cache on install
const PRECACHE_ASSETS = [
  '/',
  '/static/index.html',
  '/static/manifest.json',
  '/static/idb.js',
  '/static/vedic_wasm.js',
  '/static/webllm_adapter.js',
  '/localization/dicts/hi.json',
  '/localization/dicts/bn.json',
  '/localization/dicts/as.json',
];

// API routes that should always try network first, fall back to cache
const NETWORK_FIRST_PATTERNS = [
  /\/api\/v1\/plan/,
  /\/api\/v1\/sync/,
  /\/api\/v1\/slm/,
  /\/api\/v1\/weather/,
  /\/api\/v1\/ndvi/,
  /\/ws\//,
];

// ── Install: pre-cache all listed assets ────────────────────────────────────
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => {
      return Promise.allSettled(
        PRECACHE_ASSETS.map((url) =>
          cache.add(url).catch((err) => {
            console.warn(`[SW] Pre-cache failed for ${url}:`, err.message);
          })
        )
      );
    }).then(() => self.skipWaiting())
  );
});

// ── Activate: delete stale caches ───────────────────────────────────────────
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_VERSION)
          .map((key) => {
            console.log('[SW] Deleting old cache:', key);
            return caches.delete(key);
          })
      )
    ).then(() => self.clients.claim())
  );
});

// ── Fetch: Cache-First for static assets, Network-First for API ─────────────
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Skip non-GET requests and WebSockets
  if (event.request.method !== 'GET') return;
  if (url.protocol === 'ws:' || url.protocol === 'wss:') return;

  // Network-first for API routes (fresh data when online)
  const isApi = NETWORK_FIRST_PATTERNS.some((pattern) => pattern.test(url.pathname));
  if (isApi) {
    event.respondWith(networkFirst(event.request));
    return;
  }

  // Cache-first for everything else (static assets, localization JSON, root)
  event.respondWith(cacheFirst(event.request));
});

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_VERSION);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    // Return offline fallback page if root is requested
    const fallback = await caches.match('/');
    return fallback || new Response('Krishi-Veda is offline. Please connect to the internet.', {
      status: 503,
      headers: { 'Content-Type': 'text/plain' },
    });
  }
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_VERSION);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    if (cached) return cached;
    return new Response(JSON.stringify({ error: 'offline', cached: false }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
