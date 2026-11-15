
(() => {
  "use strict";

  const grid = document.getElementById("nexataFeedGrid");

  if (!grid) {
    console.error("SLUPMX: No se encontró el elemento nexataFeedGrid.");
    return;
  }

  const escapeHTML = value =>
    String(value ?? "").replace(/[&<>"']/g, char => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;"
    }[char]));

  const safeURL = value => {
    try {
      const url = new URL(value, window.location.href);
      return ["https:", "http:"].includes(url.protocol)
        ? url.href
        : "";
    } catch {
      return "";
    }
  };

  const formatDate = value => {
    if (!value) return "";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) return "";

    return new Intl.DateTimeFormat("es-MX", {
      day: "numeric",
      month: "long",
      year: "numeric"
    }).format(date);
  };

  async function loadNexataFeed() {
    try {
      grid.innerHTML =
        '<p class="rss-status">Cargando publicaciones...</p>';

      const feedURL = new URL(
        "data/nexata-products.json",
        document.baseURI
      );

      const response = await fetch(feedURL, {
        cache: "no-store"
      });

      if (!response.ok) {
        throw new Error(
          `Error HTTP ${response.status} al cargar el RSS`
        );
      }

      const posts = await response.json();

      if (!Array.isArray(posts)) {
        throw new Error("El archivo JSON no contiene una lista válida.");
      }

      const validPosts = posts.filter(post =>
        post &&
        typeof post.title === "string" &&
        post.title.trim() &&
        safeURL(post.link)
      );

      if (!validPosts.length) {
        grid.innerHTML =
          '<p class="rss-status">Próximamente encontrarás nuevas publicaciones.</p>';
        return;
      }

      grid.innerHTML = validPosts.map(post => {
        const link = safeURL(post.link);
        const image = safeURL(post.image);

        return `
          <article class="nuvary-rss-card">

            ${image ? `
              <a href="${escapeHTML(link)}"
                 target="_blank"
                 rel="noopener noreferrer">
                <img
                  class="nuvary-rss-image"
                  src="${escapeHTML(image)}"
                  alt="${escapeHTML(post.title)}"
                  loading="lazy">
              </a>
            ` : ""}

            <div class="nuvary-rss-content">

              <div class="nuvary-rss-meta">
                ${escapeHTML(post.source || "NEXATA")}
                ${post.date
                  ? " · " + escapeHTML(formatDate(post.date))
                  : ""}
              </div>

              <h3>${escapeHTML(post.title)}</h3>

              <p>
                ${escapeHTML(
                  post.description ||
                  "Consulta esta publicación en el sitio original."
                )}
              </p>

              <a class="nuvary-rss-link"
                 href="${escapeHTML(link)}"
                 target="_blank"
                 rel="noopener noreferrer">
                Leer publicación
                <span aria-hidden="true">→</span>
              </a>

            </div>
          </article>
        `;
      }).join("");

      console.log(
        "SLUPMX: publicaciones de NEXATA mostradas:",
        validPosts.length
      );

    } catch (error) {
      console.error("SLUPMX NEXATA RSS:", error);

      grid.innerHTML =
        '<p class="rss-status">No fue posible cargar las publicaciones en este momento.</p>';
    }
  }

  loadNexataFeed();

})();
