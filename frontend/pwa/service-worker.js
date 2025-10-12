self.addEventListener('install', (e) => {
  e.waitUntil(caches.open('aurora-cache-v1').then(cache => cache.addAll([
    '/', '/dashboard', '/dashboard/progress', '/manifest.webmanifest'
  ])));
});
self.addEventListener('activate', (e) => { self.clients.claim(); });
self.addEventListener('fetch', (e) => {
  e.respondWith(caches.match(e.request).then(resp => resp || fetch(e.request)));
});