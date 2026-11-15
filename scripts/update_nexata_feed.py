
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET
from pathlib import Path
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urlparse
import json
import re

CONFIG = Path("data/rss-sources.json")
OUTPUT = Path("data/nexata-products.json")
USER_AGENT = "SLUPMX-RSS-Importer/2.0"
# recuerda es aqui--------------------------------------------------------------------------------------------------------------
# Artículos de NEXATA que quieres mostrar en SLUPMX.
# Puedes agregar más enlaces sin escribir títulos ni imágenes.
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
    return re.sub(r"\s+", " ", parser.get_text()).strip()


def get_text(element, *names):
    for name in names:
        for node in element.iter():
            if node.tag.split("}")[-1].lower() == name.lower():
                if node.text and node.text.strip():
                    return node.text.strip()
    return ""


def get_link(element):
    link = get_text(element, "link")

    if link.startswith(("https://", "http://")):
        return link

    for node in element.iter():
        if node.tag.split("}")[-1].lower() == "link":
            href = node.attrib.get("href", "")
            rel = node.attrib.get("rel", "alternate")

            if href.startswith(("https://", "http://")) and rel == "alternate":
                return href

    return ""


def get_image(element):
    image_tags = ("content", "thumbnail", "enclosure")

    for node in element.iter():
        tag = node.tag.split("}")[-1].lower()

        if tag in image_tags:
            image_url = node.attrib.get("url", "")

            if image_url.startswith(("https://", "http://")):
                return image_url

    return ""


def get_source_name(root, feed_url):
    for node in root.iter():
        if node.tag.split("}")[-1].lower() in ("channel", "feed"):
            name = get_text(node, "title")

            if name:
                return name

    return urlparse(feed_url).netloc


def read_feed(feed_url):
    request = Request(
        feed_url,
        headers={"User-Agent": USER_AGENT}
    )

    with urlopen(request, timeout=30) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    source = get_source_name(root, feed_url)

    entries = []

    for item in root.iter():
        tag = item.tag.split("}")[-1].lower()

        if tag not in ("item", "entry"):
            continue

        title = get_text(item, "title")
        link = get_link(item)

        # Importar únicamente los artículos seleccionados.
        if link not in SELECTED_ARTICLES:
            continue

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
            continue

        entries.append({
            "title": clean_text(title),
            "link": link,
            "description": clean_text(description),
            "image": image,
            "date": date,
            "source": source
        })

    return entries


def main():
    if not CONFIG.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo {CONFIG}"
        )

    feeds = json.loads(CONFIG.read_text(encoding="utf-8"))

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
            print(f"Dirección ignorada: {feed_url}")
            continue

        try:
            posts = read_feed(feed_url)
            all_posts.extend(posts)
            successful_feeds += 1

            print(
                f"{feed_url}: {len(posts)} artículos seleccionados."
            )

        except Exception as error:
            print(f"Error al leer {feed_url}: {error}")

    if successful_feeds == 0:
        raise RuntimeError(
            "No se pudo leer ninguna fuente RSS. "
            "Se conserva el archivo anterior."
        )

    unique_posts = []
    seen_links = set()

    for post in all_posts:
        link = post["link"]

        if link in seen_links:
            continue

        seen_links.add(link)
        unique_posts.append(post)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT.write_text(
        json.dumps(unique_posts, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    print("--------------------------------")
    print(f"Publicaciones guardadas: {len(unique_posts)}")
    print(f"Archivo actualizado: {OUTPUT}")
    print("--------------------------------")


if __name__ == "__main__":
    main()
