
const CACHE_VERSION = "slupmx-v2";

const CORE = [
  "./",
  "./index.html",
  "./css/style.css?v=1.0.0",
  "./css/feed.global.css?v=1.0.0",
  "./js/config.js?v=1.0.0",
  "./js/productos.js?v=1.0.0",
  "./js/plataformas.js?v=1.0.0",
  "./js/publicaciones.js?v=1.0.0",
  "./js/app.js?v=1.0.0",
  "./js/feed.global.js?v=1.0.0",
  "./data/nexata-products.json"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then(cache => cache.addAll(CORE))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys()
      .then(keys =>
        Promise.all(
          keys
            .filter(key => key !== CACHE_VERSION)
            .map(key => caches.delete(key))
        )
      )
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", event => {
  const request = event.request;

  if (
    request.method !== "GET" ||
    new URL(request.url).origin !== self.location.origin
  ) {
    return;
  }

  event.respondWith(
    fetch(request)
      .then(response => {
        if (response.ok) {
          const copy = response.clone();

          caches.open(CACHE_VERSION)
            .then(cache => cache.put(request, copy));
        }

        return response;
      })
      .catch(async () => {
        const cached = await caches.match(request);

        return cached || new Response(
          "Recurso no disponible.",
          { status: 503 }
        );
      })
  );
});
