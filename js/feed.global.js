
(() => {
  "use strict";

  // Identificador correcto según el HTML de SLUPMX
  const grid = document.getElementById("nexataFeedGrid");
  if (!grid) {
    console.error("SLUPMX: No se encontró nexataFeedGrid.");
    return;
  }

  const escapeHTML = value => String(value ?? "").replace(/[&<>"']/g, char => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  }[char]));

  const safeURL = value => {
    try {
      const url = new URL(value, window.location.href);
      return ["https:", "http:"].includes(url.protocol) ? url.href : "";
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
      const response = await fetch("./data/nexata-products.json", {
        cache: "no-store"
      });

      if (!response.ok) {
        throw new Error("No se pudo cargar nexata-products.json");
      }

      const posts = await response.json();

      const validPosts = Array.isArray(posts)
        ? posts.filter(post => post && safeURL(post.link) && post.title)
        : [];

      if (!validPosts.length) {
        grid.innerHTML =
          '<p class="rss-status">Próximamente encontrarás nuevas recomendaciones.</p>';
        return;
      }

      grid.innerHTML = validPosts.map(post => {
        const link = safeURL(post.link);

        return `
          <article class="nuvary-rss-card">
            <div class="nuvary-rss-meta">
              ${escapeHTML(post.source || "NEXATA")}
              ${post.date ? " · " + escapeHTML(formatDate(post.date)) : ""}
            </div>

            <h3>${escapeHTML(post.title)}</h3>

            <p>${escapeHTML(
              post.description ||
              "Consulta esta recomendación en la publicación original."
            )}</p>

            <a class="nuvary-rss-link"
               href="${escapeHTML(link)}"
               target="_blank"
               rel="noopener noreferrer">
              Leer recomendación <span aria-hidden="true">→</span>
            </a>
          </article>
        `;
      }).join("");

    } catch (error) {
      console.error("SLUPMX NEXATA RSS:", error);

      grid.innerHTML =
        '<p class="rss-status">No fue posible cargar las recomendaciones en este momento.</p>';
    }
  }

  loadNexataFeed();
})();
