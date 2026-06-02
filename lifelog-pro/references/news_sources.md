# LifeLog Pro · 新闻来源与抓取规范 v3

## ⚠️ 环境判断（Phase 4 执行前必读）

| 运行环境 | 可用方法 | 优先策略 |
|---------|---------|---------|
| Claude.ai / Claude app | 内置 `web_search` 工具 | **web_search**（沙盒屏蔽外部RSS）|
| Claude Code（本地终端）| bash RSS + GitHub API + web_search | **GitHub Trending + GitHub API** 为主 |
| Codex（桌面）| bash RSS + GitHub API + web_search | **GitHub Trending + GitHub API** 为主 |

**重要提醒**：本 skill 的主要调用方是 Codex 和 Claude Code 本地运行环境，因此脚本以 bash/Python 直接抓取为主，web_search 为辅助降级策略。

---

## 策略 A：GitHub Trending + GitHub API（本地环境首选，实测稳定）

### A1 · GitHub Trending 页面解析（无需API Key，实测 2026-06-02 可用）

```bash
python3 - << 'PYEOF'
import urllib.request, re, json

def fetch_github_trending(since='daily', lang=''):
    url = f'https://github.com/trending{("?since="+since+("&l="+lang if lang else ""))}'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode('utf-8', errors='ignore')
    articles = re.findall(r'<article[^>]*Box-row[^>]*>(.*?)</article>', html, re.DOTALL)
    results = []
    for art in articles[:8]:
        name  = re.search(r'href="/([^/]+/[^/"]+)"', art)
        desc  = re.search(r'<p[^>]*>\s*([^<]{10,200}?)\s*</p>', art)
        lang_ = re.search(r'itemprop="programmingLanguage">([^<]+)<', art)
        stars = re.search(r'([0-9,]+)\s*stars today', art)
        if name:
            results.append({
                'repo':  name.group(1).strip(),
                'desc':  desc.group(1).strip()[:120] if desc else '',
                'lang':  lang_.group(1).strip() if lang_ else '',
                'stars_today': stars.group(1) if stars else '?',
                'url':   f"https://github.com/{name.group(1).strip()}"
            })
    return results

results = fetch_github_trending()
print(json.dumps(results, ensure_ascii=False, indent=2))
PYEOF
```

### A2 · GitHub API 近期热门 AI/LLM 项目（实测 2026-06-02 可用）

```bash
python3 - << 'PYEOF'
import urllib.request, json
from datetime import datetime, timedelta

def fetch_github_ai_hot(days_back=7, per_page=5):
    since = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    queries = [
        f'topic:llm+pushed:>{since}',
        f'topic:ai-agent+pushed:>{since}',
        f'topic:claude+created:>{since}',
    ]
    all_items = []
    seen = set()
    for q in queries:
        url = f'https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page={per_page}'
        req = urllib.request.Request(url, headers={
            'User-Agent': 'lifelog-pro/3.0',
            'Accept': 'application/vnd.github.v3+json'
        })
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read())
            for item in data.get('items', []):
                if item['full_name'] not in seen:
                    seen.add(item['full_name'])
                    all_items.append({
                        'repo': item['full_name'],
                        'desc': (item['description'] or '')[:120],
                        'stars': item['stargazers_count'],
                        'lang': item['language'] or '',
                        'url': item['html_url'],
                        'topics': item.get('topics', [])[:5],
                    })
        except Exception as e:
            print(f"Query '{q}' failed: {e}", flush=True)
    all_items.sort(key=lambda x: x['stars'], reverse=True)
    print(json.dumps(all_items[:10], ensure_ascii=False, indent=2))

fetch_github_ai_hot()
PYEOF
```

---

## 策略 B：web_search 工具（Claude.ai 环境 / 本地降级）

在 Claude.ai 中，**必须使用内置 `web_search` 工具**，每类执行1次搜索：

```
科技/AI：    "AI LLM tools release news {YYYY-MM-DD}"
财经/市场：   "tech stocks AI industry news today {YYYY-MM-DD}"
科研/学术：   "AI machine learning research paper this week"
开发者生态：  "developer tools open source release {YYYY-MM-DD}"
```

每类提取最多 **2条新闻**，格式：
```
标题：[新闻标题]
摘要：[一句话，不超过50字]
来源：[媒体名]
日期：[发布日期]
```

过滤规则：若新闻超过7天，标注"（近期相关背景，非今日）"。

---

## 策略 C：RSS Feed（本地环境可用时补充）

以下 RSS 源在用户本地机器通常可访问（不在沙盒限制内），作为补充来源：

**科技 / AI**（依序尝试）：
```
https://hnrss.org/frontpage?count=5          ← Hacker News
https://hnrss.org/newest?q=AI+LLM&count=5   ← HN AI专题
https://www.technologyreview.com/feed/
https://feeds.arstechnica.com/arstechnica/index
https://rss.arxiv.org/rss/cs.AI              ← AI论文预印本
```

**财经**（依序尝试）：
```
https://finance.yahoo.com/news/rssindex
https://feeds.marketwatch.com/marketwatch/topstories/
https://feeds.reuters.com/reuters/businessNews
```

**科学/学术**：
```
https://www.sciencedaily.com/rss/all.xml
https://phys.org/rss-feed/
https://rss.arxiv.org/rss/cs.LG
```

**健康/医学**：
```
https://feeds.bbci.co.uk/news/health/rss.xml
https://rss.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC
https://www.who.int/rss-feeds/news-english.xml
```

**国内科技**（中文用户推荐）：
```
https://36kr.com/feed
https://sspai.com/feed
https://www.ithome.com/rss/
https://www.ifanr.com/feed
```

RSS 通用抓取脚本见 `scripts/fetch_rss.py`。

---

## 完整降级决策树

```
Phase 4 开始
│
├─ 环境：Codex / Claude Code（本地）？
│   ├─ 步骤1：运行 GitHub Trending 脚本（必执行，几乎100%成功）
│   ├─ 步骤2：运行 GitHub API AI热门项目脚本（必执行）
│   ├─ 步骤3（可选）：尝试RSS Feed（成功则补充，失败则跳过）
│   └─ 步骤4（降级）：RSS全失败 → web_search 补充财经/学术新闻
│
└─ 环境：Claude.ai / Claude app？
    └─ 直接使用 web_search 工具 × 4次
        ├─ 成功 → 提取标题+摘要+来源，传给 Phase 5
        └─ 失败 → 策略 D 兜底
```

## 策略 D：兜底

若以上全部失败：
1. 基于 AI/技术行业常识生成专家建议
2. 每位专家卡片标注：`（今日实时新闻暂未获取，基于行业背景判断）`
3. 不影响日志其他模块生成

---

## 新闻数据质量标准

传入专家委员会前，每类至少需要 **1条有具体标题的新闻**。若只有 GitHub Trending 数据，也可以作为「科技新闻」使用——trending repo 本身就是行业信号。

```
最低有效格式：
{
  "tech": [
    {"title": "microsoft/markitdown", "desc": "Python工具将Office/文档转Markdown", "stars_today": "3086", "source": "GitHub Trending"},
  ],
  "finance": [],   ← 空数组时，对应专家标注"（财经新闻暂未获取）"
  "science": [],
  "health": []
}
```
