from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone
import json

FEED_URL = "https://nexata.site/feed.xml"
OUTPUT = Path("data/nexata-products.json")

def text_of(parent, tag):
    node = parent.find(tag)
    return (node.text or "").strip() if node is not None else ""

def main():
    request = Request(FEED_URL, headers={"User-Agent": "SLUPMX-RSS-Importer/1.0"})
    with urlopen(request, timeout=30) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    channel = root.find("channel")
    if channel is None:
        raise RuntimeError("El RSS no contiene un canal válido.")

    items = []
    for item in channel.findall("item"):
        title = text_of(item, "title")
        link = text_of(item, "link")
        description = text_of(item, "description")
        pub_date = text_of(item, "pubDate")
        if not title or not link.startswith(("https://", "http://")):
            continue

        items.append({
            "title": title,
            "link": link,
            "description": description,
            "date": pub_date,
            "source": "NEXATA"
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(items, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    print(f"Se guardaron {len(items)} publicaciones en {OUTPUT}")

if __name__ == "__main__":
    main()
