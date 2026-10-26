"""Build docs/feed.xml (podcast RSS) from published episodes.

An episode is listed when episodes/<name>/meta.json has "publish": true and
episodes/<name>/episode.json exists (written after production). Audio files
are GitHub release assets; the feed itself is served by GitHub Pages from docs/.
"""
import email.utils, json, os, pathlib, datetime
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "podcast.json").read_text(encoding="utf-8"))
REPO = os.environ.get("GITHUB_REPOSITORY", "OWNER/rega-shel-mishpat")
OWNER, NAME = REPO.split("/")
SITE = f"https://{OWNER.lower()}.github.io/{NAME}"


def rfc2822(date_str):
    d = datetime.datetime.fromisoformat(date_str).replace(
        hour=6, minute=0, tzinfo=datetime.timezone(datetime.timedelta(hours=2)))
    return email.utils.format_datetime(d)


def item(name, meta, info):
    url = f"https://github.com/{REPO}/releases/download/ep-{name}/{info['file']}"
    desc = meta["description"] + "\n\nהמקורות:\n" + "\n".join(
        f"{s['title']}: {s['url']}" for s in meta.get("sources", []))
    return f"""    <item>
      <title>{escape(meta['title'])}</title>
      <description><![CDATA[{desc}]]></description>
      <pubDate>{rfc2822(meta['date'])}</pubDate>
      <guid isPermaLink="false">ep-{escape(name)}</guid>
      <enclosure url="{escape(url)}" length="{info['bytes']}" type="audio/mpeg"/>
      <itunes:duration>{info['duration_seconds']}</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
      <itunes:episodeType>full</itunes:episodeType>
    </item>"""


def main():
    items = []
    for ep in sorted((ROOT / "episodes").iterdir(), reverse=True):
        meta_f, info_f = ep / "meta.json", ep / "episode.json"
        if not (meta_f.exists() and info_f.exists()):
            continue
        meta = json.loads(meta_f.read_text(encoding="utf-8"))
        if meta.get("publish"):
            items.append(item(ep.name, meta, json.loads(info_f.read_text(encoding="utf-8"))))
    cover = f"{SITE}/{pathlib.Path(CFG['cover_file']).name}"
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{escape(CFG['title'])}</title>
    <link>{SITE}/</link>
    <atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
    <language>{CFG['language']}</language>
    <description>{escape(CFG['description'])}</description>
    <itunes:author>{escape(CFG['author'])}</itunes:author>
    <itunes:owner>
      <itunes:name>{escape(CFG['owner_name'])}</itunes:name>
      <itunes:email>{escape(CFG['owner_email'])}</itunes:email>
    </itunes:owner>
    <itunes:image href="{cover}"/>
    <itunes:category text="{escape(CFG['category'])}"/>
    <itunes:explicit>{str(CFG['explicit']).lower()}</itunes:explicit>
    <itunes:type>episodic</itunes:type>
{chr(10).join(items)}
  </channel>
</rss>
"""
    out = ROOT / "docs" / "feed.xml"
    out.parent.mkdir(exist_ok=True)
    out.write_text(feed, encoding="utf-8")
    print(f"feed.xml: {len(items)} published episode(s)")


if __name__ == "__main__":
    main()
