/* Caché básica de archivos estáticos. Incrementa CACHE_VERSION al publicar cambios. */
const CACHE_VERSION = "slupmx-v1";
const CORE = ["./", "./index.html", "./css/style.css?v=1.0.0", "./js/config.js?v=1.0.0",
  "./js/productos.js?v=1.0.0", "./js/plataformas.js?v=1.0.0",
  "./js/publicaciones.js?v=1.0.0", "./js/app.js?v=1.0.0"];
self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE_VERSION).then(cache => cache.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", event => {
  const req = event.request;
  if (req.method !== "GET" || new URL(req.url).origin !== self.location.origin) return;
  event.respondWith(caches.match(req).then(cached => {
    const network = fetch(req).then(response => {
      if (response.ok) { const copy = response.clone(); caches.open(CACHE_VERSION).then(cache => cache.put(req, copy)); }
      return response;
    }).catch(() => cached);
    return cached || network;
  }));
});
