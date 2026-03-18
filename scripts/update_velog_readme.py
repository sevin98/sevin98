import re
import html
import textwrap
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

RSS_URL = "https://v2.velog.io/rss/sevin98"
README_PATH = "README.md"
MAX_POSTS = 4

START_MARKER = "<!-- BLOG-POST-LIST:START -->"
END_MARKER = "<!-- BLOG-POST-LIST:END -->"


def fetch_rss(url: str) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/xml,application/xml"
        }
    )
    with urlopen(req) as response:
        return response.read().decode("utf-8")


def truncate(text: str, max_len: int) -> str:
    return text if len(text) <= max_len else text[: max_len - 1] + "…"


def parse_rss(xml_text: str):
    root = ET.fromstring(xml_text)
    channel = root.find("channel")
    if channel is None:
        return []

    items = []
    for item in channel.findall("item")[:MAX_POSTS]:
        title = item.findtext("title", default="No title").strip()
        link = item.findtext("link", default="#").strip()
        pub_date = item.findtext("pubDate", default="").strip()
        items.append({
            "title": title,
            "link": link,
            "pub_date": pub_date,
        })
    return items


def render_cards(items):
    if not items:
        return (
            '<p align="center">아직 불러온 글이 없습니다.</p>'
        )

    blocks = []
    for post in items:
        safe_title = html.escape(truncate(post["title"], 52))
        safe_link = html.escape(post["link"], quote=True)

        block = f"""
<table>
  <tr>
    <td width="100%">
      <a href="{safe_link}">
        <img width="14" alt="post" src="https://img.icons8.com/fluency-systems-filled/48/20C997/document.png" />
        <b>{safe_title}</b>
      </a>
    </td>
  </tr>
</table>
"""
        blocks.append(textwrap.dedent(block).strip())

    return "\n<br/>\n".join(blocks)


def replace_section(readme_text: str, new_content: str) -> str:
    pattern = re.compile(
        rf"({re.escape(START_MARKER)})(.*)({re.escape(END_MARKER)})",
        re.DOTALL
    )
    replacement = f"{START_MARKER}\n{new_content}\n{END_MARKER}"
    return pattern.sub(replacement, readme_text)


def main():
    rss_text = fetch_rss(RSS_URL)
    items = parse_rss(rss_text)
    rendered = render_cards(items)

    with open(README_PATH, "r", encoding="utf-8") as f:
        readme = f.read()

    updated = replace_section(readme, rendered)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated)

    print("README updated successfully.")


if __name__ == "__main__":
    main()