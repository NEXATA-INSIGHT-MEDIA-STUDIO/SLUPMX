
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET
from pathlib import Path
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urlparse, urlunparse
import json
import re

# CONFIGURACIÓN
CONFIG = Path("data/rss-sources.json")
OUTPUT = Path("data/nexata-products.json")
USER_AGENT = "SLUPMX-RSS-Importer/3.0"

# ==================================================
# ARTÍCULOS DE NEXATA QUE SE MOSTRARÁN EN SLUPMX
# Agrega aquí los enlaces que quieras importar.
# No necesitas escribir títulos ni imágenes.
# ==================================================

SELECTED_ARTICLES = {
    "https://nexata.site/BLOGS/10.html",
    "https://nexata.site/BLOGS/15.html",
}


class HTMLText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def get_text(self):
        return " ".join(self.parts)


def clean_text(value):
    if not value:
        return ""

    parser = HTMLText()
    parser.feed(unescape(value))

    return re.sub(
        r"\s+",
        " ",
        parser.get_text()
    ).strip()


def normalize_url(url):
    """Normaliza enlaces para evitar diferencias de formato."""
    if not url:
        return ""

    url = unescape(url).strip()

    parsed = urlparse(url)

    return urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path.rstrip("/"),
        parsed.params,
        parsed.query,
        ""
    ))


SELECTED_NORMALIZED = {
    normalize_url(url)
    for url in SELECTED_ARTICLES
}


def get_text(element, *names):
    for name in names:
        for node in element.iter():
            tag = node.tag.split("}")[-1].lower()

            if tag == name.lower():
                if node.text and node.text.strip():
                    return node.text.strip()

    return ""


def get_link(element):
    # RSS tradicional
    link = get_text(element, "link")

    if link.startswith(("https://", "http://")):
        return link.strip()

    # Atom
    for node in element.iter():
        if node.tag.split("}")[-1].lower() == "link":
            href = node.attrib.get("href", "")
            rel = node.attrib.get("rel", "alternate")

            if (
                href.startswith(("https://", "http://"))
                and rel == "alternate"
            ):
                return href.strip()

    return ""


def get_image(element):
    # Buscar imágenes en RSS Media, Atom y enclosure.
    image_tags = ("content", "thumbnail", "enclosure")

    for node in element.iter():
        tag = node.tag.split("}")[-1].lower()

        if tag not in image_tags:
            continue

        image_url = node.attrib.get("url", "")

        if not image_url:
            image_url = node.attrib.get("href", "")

        if image_url.startswith(("https://", "http://")):
            return image_url.strip()

    return ""


def get_source_name(root, feed_url):
    for node in root.iter():
        if node.tag.split("}")[-1].lower() in ("channel", "feed"):
            name = get_text(node, "title")

            if name:
                return name

    return urlparse(feed_url).netloc


def read_feed(feed_url):
    print()
    print("Leyendo RSS:", feed_url)

    request = Request(
        feed_url,
        headers={"User-Agent": USER_AGENT}
    )

    with urlopen(request, timeout=30) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    source = get_source_name(root, feed_url)

    entries = []
    found_articles = 0

    for item in root.iter():
        tag = item.tag.split("}")[-1].lower()

        if tag not in ("item", "entry"):
            continue

        title = get_text(item, "title")
        link = get_link(item)

        normalized_link = normalize_url(link)

        print("Artículo encontrado:", link)

        # Importar únicamente los artículos seleccionados.
        if normalized_link not in SELECTED_NORMALIZED:
            print("No seleccionado.")
            continue

        found_articles += 1

        description = get_text(
            item,
            "description",
            "summary",
            "encoded"
        )

        date = get_text(
            item,
            "pubdate",
            "published",
            "updated",
            "date"
        )

        image = get_image(item)

        if not title or not link:
            print("Artículo omitido: falta título o enlace.")
            continue

        entries.append({
            "title": clean_text(title),
            "link": link,
            "description": clean_text(description),
            "image": image,
            "date": date,
            "source": source
        })

        print("IMPORTADO:", title)
        print("IMAGEN:", image or "No se encontró imagen")

    print("Artículos seleccionados encontrados:", found_articles)
    print("Artículos importados:", len(entries))

    return entries


def main():
    if not CONFIG.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo {CONFIG}"
        )

    feeds = json.loads(
        CONFIG.read_text(encoding="utf-8")
    )

    if not isinstance(feeds, list) or not feeds:
        raise ValueError(
            "rss-sources.json debe contener una lista de direcciones RSS."
        )

    all_posts = []
    successful_feeds = 0

    for feed_url in feeds:
        if not isinstance(feed_url, str):
            continue

        feed_url = feed_url.strip()

        if not feed_url.startswith(("https://", "http://")):
            print("Dirección ignorada:", feed_url)
            continue

        try:
            posts = read_feed(feed_url)

            all_posts.extend(posts)
            successful_feeds += 1

        except Exception as error:
            print("Error al leer", feed_url, ":", error)

    if successful_feeds == 0:
        raise RuntimeError(
            "No se pudo leer ninguna fuente RSS. "
            "Se conserva el archivo anterior."
        )

    # Evitar publicaciones repetidas por enlace.
    unique_posts = []
    seen_links = set()

    for post in all_posts:
        link = normalize_url(post["link"])

        if link in seen_links:
            continue

        seen_links.add(link)
        unique_posts.append(post)

    # Ordenar por fecha, si hay varias publicaciones.
    unique_posts.sort(
        key=lambda post: post.get("date", ""),
        reverse=True
    )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT.write_text(
        json.dumps(
            unique_posts,
            ensure_ascii=False,
            indent=2
        ) + "\n",
        encoding="utf-8"
    )

    print()
    print("--------------------------------")
    print("IMPORTACIÓN TERMINADA")
    print("Publicaciones guardadas:", len(unique_posts))
    print("Archivo actualizado:", OUTPUT)
    print("--------------------------------")


if __name__ == "__main__":
    main()
