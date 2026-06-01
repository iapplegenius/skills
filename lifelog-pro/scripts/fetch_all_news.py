#!/usr/bin/env python3
"""一键抓取全部四类新闻 - Phase 4 专用 · LifeLog Pro v2"""
import urllib.request, xml.etree.ElementTree as ET, json, sys, os

def fetch_rss(url, max_items=3, timeout=10):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; LifeLogPro/2.0)'})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            content = r.read()
        root = ET.fromstring(content)
        ns_atom = {'atom': 'http://www.w3.org/2005/Atom'}
        items = []
        for item in root.findall('.//item')[:max_items]:
            title = (item.findtext('title') or '').strip()
            desc  = (item.findtext('description') or '')[:300].strip()
            link  = (item.findtext('link') or '').strip()
            date  = (item.findtext('pubDate') or '').strip()
            if title: items.append({'title': title, 'desc': desc, 'link': link, 'date': date})
        if not items:
            for entry in root.findall('atom:entry', ns_atom)[:max_items]:
                title = (entry.findtext('atom:title', '', ns_atom) or '').strip()
                summ  = (entry.findtext('atom:summary', '', ns_atom) or '')[:300].strip()
                link_el = entry.find('atom:link', ns_atom)
                link  = link_el.get('href', '') if link_el is not None else ''
                date  = (entry.findtext('atom:updated', '', ns_atom) or '').strip()
                if title: items.append({'title': title, 'desc': summ, 'link': link, 'date': date})
        return {'status': 'ok', 'source': url, 'items': items}
    except Exception as e:
        return {'status': 'error', 'source': url, 'error': str(e), 'items': []}

def try_feeds(feeds, category, max_items=3):
    for url in feeds:
        result = fetch_rss(url, max_items)
        if result['status'] == 'ok' and result['items']:
            result['category'] = category
            print(f"✅ [{category}] {url}", file=sys.stderr)
            return result
        print(f"❌ [{category}] {url}: {result.get('error','empty')}", file=sys.stderr)
    return {'category': category, 'status': 'all_failed', 'items': [], 'source': 'none'}

NEWS_PLAN = {
    'tech': [
        "https://hnrss.org/frontpage?count=5",
        "https://hnrss.org/newest?q=AI+LLM&count=5",
        "https://www.technologyreview.com/feed/",
        "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
    ],
    'finance': [
        "https://finance.yahoo.com/news/rssindex",
        "https://feeds.marketwatch.com/marketwatch/topstories/",
        "https://feeds.reuters.com/reuters/businessNews",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    ],
    'science': [
        "https://www.sciencedaily.com/rss/all.xml",
        "https://phys.org/rss-feed/",
        "https://www.nature.com/nature.rss",
        "https://rss.arxiv.org/rss/cs.AI",
    ],
    'health': [
        "https://feeds.bbci.co.uk/news/health/rss.xml",
        "https://rss.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC",
        "https://www.health.harvard.edu/blog/feed",
        "https://www.medicalnewstoday.com/rss",
    ]
}

os.makedirs('/tmp/lifelog-collect', exist_ok=True)
results = {cat: try_feeds(feeds, cat) for cat, feeds in NEWS_PLAN.items()}
output_path = '/tmp/lifelog-collect/news_data.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(json.dumps(results, ensure_ascii=False, indent=2))
print(f"\n💾 Saved to {output_path}", file=sys.stderr)
