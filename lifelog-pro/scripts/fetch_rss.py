#!/usr/bin/env python3
"""RSS/Atom Feed 抓取器 - 无需第三方库 · LifeLog Pro v2"""
import urllib.request, xml.etree.ElementTree as ET, json, sys

def fetch_rss(url, max_items=3, timeout=10):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; LifeLogPro/2.0)'
        })
        with urllib.request.urlopen(req, timeout=timeout) as r:
            content = r.read()
        root = ET.fromstring(content)
        ns_atom = {'atom': 'http://www.w3.org/2005/Atom'}
        items = []
        for item in root.findall('.//item')[:max_items]:
            title = (item.findtext('title') or '').strip()
            desc  = (item.findtext('description') or '')[:300].strip()
            link  = (item.findtext('link') or '').strip()
            date  = (item.findtext('pubDate') or item.findtext('dc:date') or '').strip()
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

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else ''
    n   = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    print(json.dumps(fetch_rss(url, n), ensure_ascii=False, indent=2))
