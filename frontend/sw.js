/**
 * Krishi-Veda Service Worker — Offline-First PWA
 * - Cache-first for static assets (HTML, JS, CSS, JSON dicts)
 * - Network-first for API calls with offline fallback
 * - Caches /api/v1/plan POST responses by request body hash
 * - Shows offline banner when network unavailable
 */

const CACHE_VERSION = 'krishi-veda-v4';
const OFFLINE_BANNER_KEY = 'krishi-veda-offline';

// Static assets to pre-cache on install
const PRECACHE_ASSETS = [
  '/',
  '/static/index.html',
  '/static/manifest.json',
  '/localization/dicts/hi.json',
  '/localization/dicts/bn.json',
  '/localization/dicts/as.json',
];

// API routes that use network-first with offline fallback
const API_PATTERNS = [
  /\/api\/v1\/plan/,
  /\/api\/v1\/sync/,
  /\/api\/v1\/slm/,
  /\/api\/v1\/weather/,
  /\/api\/v1\/ndvi/,
];

// ── Install: pre-cache static assets ─────────────────────────────────────
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

// ── Activate: clean old caches, notify clients about offline-ready state ──
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_VERSION && key !== OFFLINE_BANNER_KEY)
          .map((key) => {
            console.log('[SW] Deleting old cache:', key);
            return caches.delete(key);
          })
      )
    ).then(() => self.clients.claim())
  );
});

// ── Message: listen for offline banner requests from the page ────────────
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'CHECK_ONLINE') {
    // Respond with online status
    event.ports[0]?.postMessage({ online: self.navigator?.onLine ?? true });
  }
});

// ── Fetch: route to appropriate strategy ─────────────────────────────────
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Skip non-GET/POST and WebSockets
  if (!['GET', 'POST'].includes(event.request.method)) return;
  if (url.protocol === 'ws:' || url.protocol === 'wss:') return;

  // API routes: network-first with offline fallback
  const isApi = API_PATTERNS.some((pattern) => pattern.test(url.pathname));
  if (isApi) {
    // For POST /api/v1/plan, cache by request body hash
    if (url.pathname.includes('/api/v1/plan') && event.request.method === 'POST') {
      event.respondWith(networkFirstWithBodyCache(event.request));
      return;
    }
    event.respondWith(networkFirst(event.request));
    return;
  }

  // Static assets: cache-first
  event.respondWith(cacheFirst(event.request));
});

// ── Cache-First Strategy ─────────────────────────────────────────────────
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
    // Return offline fallback for page navigation
    if (request.mode === 'navigate') {
      const fallback = await caches.match('/');
      if (fallback) return fallback;
    }
    return new Response('Krishi-Veda is offline. Please connect to the internet.', {
      status: 503,
      headers: { 'Content-Type': 'text/plain' },
    });
  }
}

// ── Network-First Strategy (basic) ───────────────────────────────────────
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

// ── Network-First with Body-Hash Cache (for POST /api/v1/plan) ───────────
async function networkFirstWithBodyCache(request) {
  try {
    const response = await fetch(request.clone());
    if (response.ok) {
      const cache = await caches.open(CACHE_VERSION);
      // Create a normalized cache key from the request body hash
      const bodyHash = await hashRequestBody(request);
      const cacheKey = new Request(`/api/v1/plan/cached/${bodyHash}`, {
        method: 'GET',
      });
      cache.put(cacheKey, response.clone());
    }
    return response;
  } catch {
    // Offline: try to find a cached response by body hash
    const bodyHash = await hashRequestBody(request);
    const cacheKey = new Request(`/api/v1/plan/cached/${bodyHash}`, {
      method: 'GET',
    });
    const cached = await caches.match(cacheKey);
    if (cached) {
      // Add offline header so the frontend can show a banner
      const headers = new Headers(cached.headers);
      headers.set('X-Krishi-Veda-Offline', 'true');
      return new Response(cached.body, {
        status: cached.status,
        statusText: cached.statusText,
        headers: headers,
      });
    }
    return new Response(JSON.stringify({ 
      error: 'offline', 
      cached: false,
      message: 'No cached plan for these inputs. Connect to the internet.'
    }), {
      status: 503,
      headers: { 
        'Content-Type': 'application/json',
        'X-Krishi-Veda-Offline': 'true'
      },
    });
  }
}

// ── Simple hash for request body (for cache key generation) ──────────────
async function hashRequestBody(request) {
  try {
    const clone = request.clone();
    const text = await clone.text();
    // Simple DJB2 hash
    let hash = 5381;
    for (let i = 0; i < text.length; i++) {
      hash = ((hash << 5) + hash) + text.charCodeAt(i);
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash).toString(16);
  } catch {
    return 'no-body';
  }
}
