import feedparser
import hashlib
import os
import datetime
import re

OUTPUT_PATH = "output/merged.xml"

def normalize_link(link: str):
    """Clean link to improve deduplication."""
    if not link:
        return ""
    link = re.sub(r"https?://(www\.)?", "", link)
    link = re.sub(r"/+$", "", link)
    return link.strip().lower()

def unique_id(entry):
    """Generate a unique fingerprint for deduplication."""
    link = normalize_link(entry.get("link", ""))
    title = entry.get("title", "").strip().lower()
    return hashlib.md5(f"{link}-{title}".encode("utf-8")).hexdigest()

def load_feeds(file="feed_urls.txt"):
    with open(file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def fetch_all_feeds(urls):
    all_entries = []
    for url in urls:
        print(f"Fetching {url}")
        feed = feedparser.parse(url)
        all_entries.extend(feed.entries)
    return all_entries

def deduplicate(entries):
    seen = set()
    unique = []
    for e in entries:
        uid = unique_id(e)
        if uid not in seen:
            seen.add(uid)
            unique.append(e)
    return unique

def make_rss(entries):
    now = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0"><channel>',
        "<title>Combined Politepol Feed</title>",
        "<link>https://yourgithubusername.github.io/rss-merge/output/merged.xml</link>",
        "<description>Merged feed from multiple Politepol sources</description>",
        f"<lastBuildDate>{now}</lastBuildDate>",
    ]
    for e in entries:
        title = e.get("title", "No title")
        link = e.get("link", "")
        desc = e.get("summary", "")
        pub = e.get("published", now)
        xml.append("<item>")
        xml.append(f"<title><![CDATA[{title}]]></title>")
        xml.append(f"<link>{link}</link>")
        xml.append(f"<pubDate>{pub}</pubDate>")
        xml.append(f"<description><![CDATA[{desc}]]></description>")
        xml.append("</item>")
    xml.append("</channel></rss>")
    return "\n".join(xml)

def main():
    urls = load_feeds()
    entries = fetch_all_feeds(urls)
    print(f"Fetched {len(entries)} total entries")
    entries = deduplicate(entries)
    print(f"{len(entries)} unique entries after deduplication")
    rss = make_rss(entries)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(rss)
    print("✅ Merged RSS saved.")

if __name__ == "__main__":
    main()
