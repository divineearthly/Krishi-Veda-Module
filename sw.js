// Krishi-Veda Service Worker
const CACHE = 'krishi-veda-v2';

self.addEventListener('install', (e) => {
    e.waitUntil(
        caches.open(CACHE).then(cache => {
            return cache.addAll([
                '/',
                '/index.html',
                '/manifest.json',
                '/farmer_ui.html'
            ]);
        })
    );
});

self.addEventListener('fetch', (e) => {
    e.respondWith(
        caches.match(e.request).then(r => r || fetch(e.request))
    );
});
