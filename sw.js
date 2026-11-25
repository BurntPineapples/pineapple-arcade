// Cache-first for game thumbnails: instant on repeat visits (the original thumbs only cache for 10 min over HTTP).
const CACHE = 'thumbs-v1', MAX = 3000;
let puts = 0;
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', e => {
  if (e.request.destination !== 'image') return;
  e.respondWith(caches.open(CACHE).then(async c => {
    const hit = await c.match(e.request.url);
    if (hit) return hit;
    // cors (all three image hosts allow it) so the cache stores a real response, not a quota-hungry opaque one
    const res = await fetch(e.request.url, { mode: 'cors' }).catch(() => fetch(e.request));
    if (res.ok && res.type === 'cors') {
      c.put(e.request.url, res.clone());
      // ponytail: crude cap, drops oldest entries every 100 new images
      if (++puts % 100 === 0) c.keys().then(k => k.slice(0, Math.max(0, k.length - MAX)).forEach(r => c.delete(r)));
    }
    return res;
  }));
});
