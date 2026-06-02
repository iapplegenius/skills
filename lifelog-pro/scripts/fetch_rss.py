#!/usr/bin/env python3
"""
LifeLog Pro v3 · 新闻抓取脚本
优先策略：GitHub Trending → GitHub API → RSS → 降级

用法：
  python3 fetch_rss.py                    # 抓取全部，输出 JSON
  python3 fetch_rss.py --category tech    # 只抓科技
  python3 fetch_rss.py --output /tmp/news.json
"""
import urllib.request, xml.etree.ElementTree as ET
import json, sys, re, os, time
from datetime import datetime, timedelta

# ── 工具函数 ──────────────────────────────────────────────

def fetch_url(url, timeout=10):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/json,*/*',
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def fetch_rss_feed(url, max_items=3):
    """通用 RSS/Atom 抓取"""
    content = fetch_url(url)
    root = ET.fromstring(content)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    items = []
    for item in root.findall('.//item')[:max_items]:
        title = (item.findtext('title') or '').strip()
        desc  = (item.findtext('description') or '')[:300].strip()
        link  = (item.findtext('link') or '').strip()
        date  = (item.findtext('pubDate') or '').strip()
        if title:
            items.append({'title': title, 'desc': desc, 'link': link, 'date': date, 'source': url})
    if not items:
        for entry in root.findall('atom:entry', ns)[:max_items]:
            title = (entry.findtext('atom:title', '', ns) or '').strip()
            summ  = (entry.findtext('atom:summary', '', ns) or '')[:300].strip()
            lel   = entry.find('atom:link', ns)
            link  = lel.get('href', '') if lel is not None else ''
            date  = (entry.findtext('atom:updated', '', ns) or '').strip()
            if title:
                items.append({'title': title, 'desc': summ, 'link': link, 'date': date, 'source': url})
    return items

# ── GitHub Trending（实测稳定，2026-06-02 验证）─────────────

def fetch_github_trending(since='daily', max_items=8):
    """解析 GitHub Trending 页面，无需 API Key"""
    url = f'https://github.com/trending?since={since}'
    html = fetch_url(url).decode('utf-8', errors='ignore')
    articles = re.findall(r'<article[^>]*Box-row[^>]*>(.*?)</article>', html, re.DOTALL)
    results = []
    for art in articles[:max_items]:
        name  = re.search(r'href="/([^/]+/[^/"]+)"', art)
        desc  = re.search(r'<p[^>]*>\s*([^<]{10,200}?)\s*</p>', art)
        lang_ = re.search(r'itemprop="programmingLanguage">([^<]+)<', art)
        stars = re.search(r'([0-9,]+)\s*stars today', art)
        if name:
            results.append({
                'title': name.group(1).strip(),
                'desc':  desc.group(1).strip()[:120] if desc else '',
                'lang':  lang_.group(1).strip() if lang_ else '',
                'stars_today': stars.group(1) if stars else '?',
                'link':  f"https://github.com/{name.group(1).strip()}",
                'source': 'GitHub Trending',
            })
    return results

# ── GitHub API（近期热门 AI/LLM 项目）──────────────────────

def fetch_github_ai_hot(days_back=7, per_page=5):
    """GitHub Search API 查询近期 AI/LLM 热门项目"""
    since = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    queries = [
        f'topic:llm+pushed:>{since}',
        f'topic:ai-agent+created:>{since}',
    ]
    seen = set()
    results = []
    for q in queries:
        url = f'https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page={per_page}'
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'lifelog-pro/3.0',
                'Accept': 'application/vnd.github.v3+json',
            })
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read())
            for item in data.get('items', []):
                if item['full_name'] not in seen:
                    seen.add(item['full_name'])
                    results.append({
                        'title': item['full_name'],
                        'desc': (item['description'] or '')[:120],
                        'stars': item['stargazers_count'],
                        'lang': item['language'] or '',
                        'link': item['html_url'],
                        'source': 'GitHub API',
                    })
        except Exception as e:
            print(f"[GitHub API] query '{q}' failed: {e}", file=sys.stderr)
    results.sort(key=lambda x: x.get('stars', 0), reverse=True)
    return results[:8]

# ── RSS 源列表 ─────────────────────────────────────────────

RSS_SOURCES = {
    'tech': [
        'https://hnrss.org/frontpage?count=5',
        'https://hnrss.org/newest?q=AI+LLM&count=5',
        'https://www.technologyreview.com/feed/',
        'https://feeds.arstechnica.com/arstechnica/index',
        'https://rss.arxiv.org/rss/cs.AI',
    ],
    'finance': [
        'https://finance.yahoo.com/news/rssindex',
        'https://feeds.marketwatch.com/marketwatch/topstories/',
        'https://feeds.reuters.com/reuters/businessNews',
    ],
    'science': [
        'https://www.sciencedaily.com/rss/all.xml',
        'https://phys.org/rss-feed/',
        'https://rss.arxiv.org/rss/cs.LG',
        'https://www.nature.com/nature.rss',
    ],
    'health': [
        'https://feeds.bbci.co.uk/news/health/rss.xml',
        'https://rss.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC',
        'https://www.who.int/rss-feeds/news-english.xml',
    ],
}

def try_rss_category(category, max_items=3):
    """依序尝试某类 RSS 源，返回第一个成功的结果"""
    for url in RSS_SOURCES.get(category, []):
        try:
            items = fetch_rss_feed(url, max_items)
            if items:
                print(f"[RSS] ✅ {category}: {url}", file=sys.stderr)
                return {'status': 'ok', 'source': url, 'items': items}
        except Exception as e:
            print(f"[RSS] ❌ {category}: {url} → {str(e)[:60]}", file=sys.stderr)
    return {'status': 'failed', 'items': []}

# ── 主函数 ─────────────────────────────────────────────────

def fetch_all_news():
    result = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'generated_at': datetime.now().isoformat(),
        'github_trending': [],
        'github_ai_hot': [],
        'rss': {'tech': {}, 'finance': {}, 'science': {}, 'health': {}},
        'status': {},
    }

    # 1. GitHub Trending（几乎100%成功）
    try:
        result['github_trending'] = fetch_github_trending()
        result['status']['github_trending'] = f"ok ({len(result['github_trending'])} repos)"
        print(f"[GitHub Trending] ✅ {len(result['github_trending'])} repos", file=sys.stderr)
    except Exception as e:
        result['status']['github_trending'] = f"failed: {e}"
        print(f"[GitHub Trending] ❌ {e}", file=sys.stderr)

    # 2. GitHub API AI 热门
    try:
        result['github_ai_hot'] = fetch_github_ai_hot()
        result['status']['github_api'] = f"ok ({len(result['github_ai_hot'])} repos)"
        print(f"[GitHub API] ✅ {len(result['github_ai_hot'])} repos", file=sys.stderr)
    except Exception as e:
        result['status']['github_api'] = f"failed: {e}"
        print(f"[GitHub API] ❌ {e}", file=sys.stderr)

    # 3. RSS 补充（可选，失败不影响主流程）
    for cat in ['tech', 'finance', 'science', 'health']:
        r = try_rss_category(cat)
        result['rss'][cat] = r
        result['status'][f'rss_{cat}'] = r['status']
        time.sleep(0.2)

    return result

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='', help='输出文件路径（默认 stdout）')
    parser.add_argument('--category', default='all', help='only: tech/finance/science/health/all')
    args = parser.parse_args()

    os.makedirs('/tmp/lifelog-collect', exist_ok=True)
    data = fetch_all_news()
    json_str = json.dumps(data, ensure_ascii=False, indent=2)

    output_path = args.output or '/tmp/lifelog-collect/news_data.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(json_str)
    print(json_str)
    print(f"\n💾 Saved → {output_path}", file=sys.stderr)
