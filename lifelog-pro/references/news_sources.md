# LifeLog Pro · 新闻来源与抓取规范 v2

## 环境判断（Phase 4 执行前必读）

不同运行环境能力不同，**必须先判断环境，再选择抓取策略**：

| 环境 | 可用方法 | 优先使用 |
|------|---------|---------|
| Claude.ai / Claude app | 内置 `web_search` 工具 | **web_search**（RSS 被沙箱屏蔽）|
| Claude Code（本地终端）| bash RSS + web_search | **RSS 脚本**（更完整更快）|
| Cowork（桌面）| bash RSS + web_search | **RSS 脚本** |

---

## 策略 A：web_search 工具（Claude.ai 默认策略）

在 Claude.ai 环境中，**使用内置 `web_search` 工具**抓取新闻，这是最可靠的方式。

### 搜索词模板（按类别各执行一次）

```
科技/AI：
  "AI LLM artificial intelligence news {YYYY-MM-DD}"
  → 备用："site:techcrunch.com OR site:theverge.com AI news today"

财经/市场：
  "stock market Nasdaq tech stocks {YYYY-MM-DD}"
  → 备用："AI industry investment funding news this week"

科学/学术：
  "science research breakthrough {YYYY-MM-DD}"
  → 备用："site:sciencedaily.com OR site:nature.com latest research"

健康/医学：
  "health medical research news {YYYY-MM-DD}"
  → 备用："site:webmd.com OR site:medicalnewstoday.com latest"
```

### 执行规范

每类执行 **1-2 次搜索**，提取最多 2 条新闻，格式：
```
标题：[新闻标题]
摘要：[一句话摘要，自己提炼，不超过50字]
来源：[发布媒体]
日期：[发布日期，必须是今天或本周内]
```

日期过滤规则：若搜索结果中新闻超过7天，标注"（本周无最新消息，引用近期相关背景）"。

---

## 策略 B：RSS Feed 脚本（Claude Code / 本地终端环境）

在有完整网络权限的环境中，使用以下 Python 脚本直接抓取 RSS，无需 API Key。

### 通用抓取脚本（`scripts/fetch_rss.py`）

```python
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
```

### 推荐 RSS 源（按类别，依可靠性排序）

**科技 / AI 新闻**：
```
https://hnrss.org/frontpage?count=5          ← Hacker News Top
https://hnrss.org/newest?q=AI+LLM&count=5   ← HN AI 专题
https://www.technologyreview.com/feed/       ← MIT Tech Review
https://www.theverge.com/ai-artificial-intelligence/rss/index.xml
https://feeds.arstechnica.com/arstechnica/index
```

**财经 / 市场新闻**：
```
https://finance.yahoo.com/news/rssindex
https://feeds.marketwatch.com/marketwatch/topstories/
https://feeds.reuters.com/reuters/businessNews
https://www.cnbc.com/id/100003114/device/rss/rss.html
```

**科学 / 学术新闻**：
```
https://www.sciencedaily.com/rss/all.xml
https://phys.org/rss-feed/
https://www.nature.com/nature.rss
https://rss.arxiv.org/rss/cs.AI             ← AI 论文预印本
https://rss.arxiv.org/rss/cs.LG             ← ML 论文预印本
```

**健康 / 医学新闻**：
```
https://feeds.bbci.co.uk/news/health/rss.xml
https://rss.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC
https://www.health.harvard.edu/blog/feed
https://www.who.int/rss-feeds/news-english.xml
```

### 一键抓取脚本（`scripts/fetch_all_news.py`）

```python
#!/usr/bin/env python3
"""一键抓取全部四类新闻 · LifeLog Pro v2"""
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
    'tech':    ["https://hnrss.org/frontpage?count=5","https://www.technologyreview.com/feed/","https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"],
    'finance': ["https://finance.yahoo.com/news/rssindex","https://feeds.marketwatch.com/marketwatch/topstories/","https://feeds.reuters.com/reuters/businessNews"],
    'science': ["https://www.sciencedaily.com/rss/all.xml","https://phys.org/rss-feed/","https://rss.arxiv.org/rss/cs.AI"],
    'health':  ["https://feeds.bbci.co.uk/news/health/rss.xml","https://rss.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC","https://www.health.harvard.edu/blog/feed"],
}

os.makedirs('/tmp/lifelog-collect', exist_ok=True)
results = {cat: try_feeds(feeds, cat) for cat, feeds in NEWS_PLAN.items()}
output = '/tmp/lifelog-collect/news_data.json'
with open(output, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(json.dumps(results, ensure_ascii=False, indent=2))
print(f"\n💾 Saved → {output}", file=sys.stderr)
```

执行：`python3 /tmp/lifelog-pro/scripts/fetch_all_news.py > /tmp/lifelog-collect/news_data.json`

---

## 策略 C：兜底（两种方法都失败时）

若 web_search 和 RSS 均无法获取有效新闻：
1. 基于行业常识生成专家建议
2. 在专家卡片上标注：`（今日新闻暂未获取，基于行业背景）`
3. 不影响其他模块的正常生成

---

## 完整降级决策树

```
Phase 4 开始
│
├─ 是 Claude.ai / Claude app？
│   └─ 使用 web_search 工具 × 4次（每类一次）
│       ├─ 成功 → 提取标题+摘要+来源，传给 Phase 5
│       └─ 失败 → 策略 C 兜底
│
└─ 是 Claude Code / 本地终端？
    └─ 运行 python3 scripts/fetch_all_news.py
        ├─ 成功（至少1类有数据）→ 传给 Phase 5
        └─ 全部失败 → 降级到 web_search → 失败再 → 策略 C 兜底
```
