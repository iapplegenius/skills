---
name: lifelog-pro
description: >
  超级个人成长日志系统 v2。自动采集本机数据（shell history、浏览器记录、软件使用、AI agent对话），
  结合历史日记进行成长关联分析，支持日报/周报/月报三种模式。
  内置"专家委员会"模块：通过 RSS Feed 抓取科技/财经/科学新闻，
  结合用户当天真实行为，由科技、商业投资、学术科学、心理健康四大领域专家
  各自给出动态建议，最后由全知综合专家汇总。
  支持 Windows / macOS / Linux 全平台自动采集。
  触发词：生成日记、生成日报、生成周报、记录今天、lifelog、lifelog-pro、
  分析我今天、整理今天、日志、成长记录、周报、本周总结，
  以及所有原 lifelog-daily 触发词。
  即使用户只说"帮我整理一下今天"也应触发此 skill。
---

# LifeLog Pro v2 · 超级成长日志

> **⚠️ 首要强制规则：在生成任何 HTML 文件之前，必须先完整阅读 `references/html_template.md`，严格使用其中定义的 HTML 骨架、CSS 类名和所有占位符，不得自行简化或替换模板。**

---

## 快速导航

| 阶段 | 说明 |
|------|------|
| Phase 0 | 判断模式（日/周/月） |
| Phase 1 | 运行自动采集脚本 |
| Phase 2 | 解析所有数据源 |
| Phase 3 | 读取历史日记·拐点分析（读 `references/history_reader.md`）|
| Phase 4 | **RSS 抓取实时新闻**（读 `references/news_sources.md`）|
| Phase 5 | 专家委员会建议（读 `references/expert_prompts.md`）|
| Phase 6 | 生成输出文件（读 `references/html_template.md`）|
| 周报模式 | 聚合7份日报（读 `references/weekly_aggregator.md`）|

---

## Phase 0 · 判断报告模式

**必须首先判断模式，后续所有步骤根据模式选择执行路径。**

| 用户说 | 模式 | 执行路径 |
|--------|------|---------|
| 日记/日报/今天/today | **日报** | 执行 Phase 1→6 |
| 周报/本周/this week | **周报** | 跳到[周报模式](#周报模式) |
| 月报/本月/this month | **月报** | 同周报逻辑，扫描30天日报 |

---

## Phase 1 · 自动采集数据

**规则：在询问用户手动提供任何内容之前，先运行自动采集脚本。**

```bash
python3 /tmp/lifelog-pro/scripts/collect.py
```

输出文件：`/tmp/lifelog-collect/collected_data.json`

采集内容（跨平台，任何一项失败自动跳过，不中断流程）：
- Shell history（bash/zsh/fish/PowerShell）
- AI Agent 对话记录（Claude Code / Cursor / Codex / Hermes）
- 浏览器历史（Chrome / Firefox / Edge / Safari）
- 软件/进程使用快照
- 命令时间间隔序列（用于能量曲线构建）
- 今日编辑文件列表
- 过去30天历史日记

**采集结束后**：向用户汇报哪些数据源成功/失败，然后继续执行 Phase 2。用户额外手动提供的内容与自动采集结果合并处理。

---

## Phase 2 · 解析数据

### 2a · Shell History + 二阶信号

**基础解析**（必须执行）：
- 命令分类：开发 / 运维 / 文件 / 网络 / 数据 / AI工具 / 其他
- 提取项目名（从路径、git仓库名、pip包名推断）
- 提取关键操作（git commit 消息、安装的包、创建的文件）
- 识别错误与重试（连续失败命令）

**无时间戳处理**：时间列填 `—`，frontmatter 标注 `terminal_history_no_timestamp`，报告开头说明"命令时间信息不可用，以顺序展示"。

**二阶信号提取**（有时间戳时必须执行）：

```
- 命令密度：每小时命令数 → 输出能量曲线数据点
- 专注块识别：连续15分钟内无 >5分钟中断 = 一个深度专注块
- 恢复速度：错误发生后多久出现成功命令
- 搜索行为：浏览器同一问题域的搜索次数（知识盲区深度）
- 工具切换频率：IDE↔浏览器↔聊天的切换次数（分心指数）
```

### 2b · AI Agent 对话解析

从采集的 agent 日志中提取：对话时长/轮次、涉及项目/任务、卡点识别（反复修正、同一问题多次询问）、使用的 agent 类型。

### 2c · 浏览器历史解析

- 分类：技术文档 / AI工具 / 社交 / 视频 / 购物 / 新闻 / 其他
- 从 Google/Bing URL 的 `q=` 参数提取搜索关键词
- 同一问题的重复搜索次数 → 知识盲区信号
- **隐私过滤**：银行/支付/登录页面 → `[已隐去敏感URL]`

### 2d · 软件使用 + 能量曲线构建

从进程快照 + 命令时间戳合并，构建能量曲线数据点和专注块列表（供 Phase 6 SVG 生成使用）。

### 全局隐私过滤

含 `password / secret / token / key / api_key` 的命令 → `[已隐去敏感内容]`

---

## Phase 3 · 历史关联与拐点分析

> **必须先阅读 `references/history_reader.md`**

### 扫描路径（按优先级）

```
1. /mnt/user-data/outputs/daily_*.md
2. ~/lifelog/daily_*.md
3. ~/Documents/lifelog/daily_*.md
4. ~/Desktop/lifelog/daily_*.md
5. ./daily_*.md
```

### 拐点识别（核心规则）

**必须输出具体数据和日期，禁止泛泛而谈：**

| 场景 | 判断条件 | 输出格式 |
|------|---------|---------|
| 专注度下滑 | 今天比前3天均值低30%以上 | "你的专注度从[日期]开始下滑，那天你[具体行为]" |
| 项目停滞 | >7天 | "停滞警告" |
| 项目搁置 | >14天 | "搁置警告" |
| 短板复现 | 历史3次以上 | "持续短板，建议专项解决" |
| 正向连续 | 连续N天专注 | "你已连续N天保持深度工作状态" |

**禁止输出示例**：`你最近一直在努力工作，继续加油` ← 此类空话一律禁止

---

## Phase 4 · 实时新闻抓取（RSS Feed 方法）

> **必须先阅读 `references/news_sources.md` 获取完整 RSS 源列表和抓取命令。**

### 核心策略：RSS Feed 直接抓取（无需 API Key）

**优先使用 bash RSS 抓取，比 web_search 更稳定、内容更完整：**

```bash
# 通用 RSS 抓取函数（Python，无需额外库）
python3 - << 'EOF'
import urllib.request, xml.etree.ElementTree as ET, json, sys

def fetch_rss(url, max_items=3):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            tree = ET.parse(r)
        root = tree.getroot()
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        items = []
        # RSS 2.0
        for item in root.findall('.//item')[:max_items]:
            title = item.findtext('title', '').strip()
            desc  = item.findtext('description', '').strip()[:200]
            link  = item.findtext('link', '').strip()
            date  = item.findtext('pubDate', item.findtext('dc:date',''))
            items.append({'title': title, 'desc': desc, 'link': link, 'date': date})
        # Atom
        if not items:
            for entry in root.findall('atom:entry', ns)[:max_items]:
                title = entry.findtext('atom:title', '', ns).strip()
                summ  = entry.findtext('atom:summary', '', ns).strip()[:200]
                link  = entry.find('atom:link', ns)
                link  = link.get('href','') if link is not None else ''
                date  = entry.findtext('atom:updated','',ns)
                items.append({'title': title, 'desc': summ, 'link': link, 'date': date})
        return items
    except Exception as e:
        return [{'error': str(e)}]

# 按需替换 URL
import sys
url = sys.argv[1] if len(sys.argv) > 1 else ''
print(json.dumps(fetch_rss(url), ensure_ascii=False, indent=2))
EOF
```

### 四类新闻各自的抓取命令（详细源见 `references/news_sources.md`）

**1. 科技 / AI 新闻**（依次尝试，取第一个成功的）：

```bash
# Hacker News Top（技术社区最热）
python3 <抓取脚本> "https://hnrss.org/frontpage?count=5"

# MIT Technology Review
python3 <抓取脚本> "https://www.technologyreview.com/feed/"

# The Verge AI
python3 <抓取脚本> "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"
```

**2. 财经 / 市场新闻**：

```bash
# Yahoo Finance
python3 <抓取脚本> "https://finance.yahoo.com/news/rssindex"

# Reuters Business
python3 <抓取脚本> "https://feeds.reuters.com/reuters/businessNews"

# MarketWatch
python3 <抓取脚本> "https://feeds.marketwatch.com/marketwatch/topstories/"
```

**3. 科学 / 学术新闻**：

```bash
# Nature News
python3 <抓取脚本> "https://www.nature.com/nature.rss"

# Science Daily
python3 <抓取脚本> "https://www.sciencedaily.com/rss/all.xml"

# Phys.org
python3 <抓取脚本> "https://phys.org/rss-feed/"
```

**4. 健康 / 医学新闻**：

```bash
# BBC Health
python3 <抓取脚本> "https://feeds.bbci.co.uk/news/health/rss.xml"

# Harvard Health Blog
python3 <抓取脚本> "https://www.health.harvard.edu/blog/feed"

# WHO News
python3 <抓取脚本> "https://www.who.int/rss-feeds/news-english.xml"
```

### 降级策略（RSS 失败时）

```
优先级：RSS Feed → web_search 备用 → 行业背景兜底

1. RSS 抓取成功 → 使用 RSS 结果
2. RSS 全部失败 → 使用 web_search 工具搜索以下词：
   - 科技："AI tech news today {YYYY-MM-DD}"
   - 财经："Nasdaq market today {YYYY-MM-DD}"
   - 科学："science research news this week"
   - 健康："health medical news this week"
3. web_search 也无结果 → 基于行业常识生成建议，
   在专家卡片上标注"（今日新闻暂未获取，基于行业背景）"
```

---

## Phase 5 · 专家委员会

> **建议阅读 `references/expert_prompts.md` 获取完整提示词模板。**

**这是本 skill 最核心的模块，必须生成五位专家的完整输出。**

### 强制规则（每位专家必须同时满足）

1. **引用至少一条用户数据的具体细节**（命令名/URL/项目名/具体时间）
2. **引用至少一条今日新闻的具体事件**（新闻标题或事件名；若新闻获取失败则标注）
3. **给出一个具体可执行的行动**：格式 "今天用X工具完成Y，预计Z分钟"
4. **字数**：每位专家正文 4-6 句；综合专家正文 6-8 句
5. **禁止空洞鼓励**："你很棒"/"继续加油" 等无意义话语一律禁止

### 五个专家角色

| 专家 | 身份 | 信息来源 | 核心输出 |
|------|------|---------|---------|
| 🔬 科技 | 硅谷工程师 + AI研究员 | Phase 4 科技新闻 + 用户开发数据 | 技术栈位置 → 行业动态影响 → 具体技术升级建议 |
| 💰 商业 | 一线投资人 + 产业分析师 | Phase 4 财经新闻 + 用户行为 | 技能/项目市场价值 → 宏观信号影响 → 建议+风险提示 |
| 🧬 学术 | 跨学科研究者 | Phase 4 科研新闻 + 浏览器学习行为 | 学术前沿位置 → 相关科研发现 → 知识体系升级 |
| 🧠 健康 | 认知科学家 + 功能医学 | Phase 2d 能量曲线 + Phase 4 健康新闻 | 能量曲线解读 → 行为心理信号 → 今晚1-2个具体行动 |
| 🌐 综合 | 超级整合视角（压轴）| 以上四位全部输出 | 串联关键信号 → 今天最重要发现 → **明天第一行动**（格式：明天[时间]，做[具体事]，预计[时长]，目标：[可验证结果]）|

---

## Phase 6 · 生成输出文件

> **⚠️ 生成 HTML 前必须阅读 `references/html_template.md`，严格使用其完整骨架和 CSS 类名。**

### Step 6a · Markdown 文件

**文件名**：`daily_YYYY-MM-DD.md`

必须包含以下所有章节，**按顺序输出**：

```markdown
---
date: {{DATE}}
generated_at: {{DATETIME}}
tags: [{{TAG_LIST}}]
data_sources: [{{SOURCES}}]
news_sources: [{{NEWS_RSS_SOURCES}}]
---

# {{DATE}} · 日志

> {{ONE_LINE_SUMMARY}}

## 今日概览

{{AI_NARRATIVE_PARAGRAPH}}

## 时间线

| 时间 | 事件 | 类型 | 详情 |
|------|------|------|------|
{{TIMELINE_ROWS}}

## 开发 / 工作记录

### 涉及项目
{{PROJECT_LIST}}

### 关键命令摘要
{{KEY_COMMANDS}}

### 命令分类统计
| 类别 | 数量 | 占比 |
|------|------|------|
{{CMD_STATS}}

{{#IF_VIDEO}}
## 视频 / 学习记录

{{VIDEO_LIST}}
{{/IF_VIDEO}}

## 今日成就

{{ACHIEVEMENTS}}

## 待续 / 未完成

{{PENDING}}

## 🎯 技能增强雷达

{{SKILL_ITEMS_MD}}

## 📈 成长轨迹

{{GROWTH_NARRATIVE}}

{{TURNING_POINTS_MD}}

## 🧠 专家委员会

### 🔬 科技专家
（引用数据：{{TECH_DATA_REF}}）（引用新闻：{{TECH_NEWS_REF}}）
{{EXPERT_TECH_MD}}
→ 今日行动：{{ACTION_TECH}}

### 💰 商业投资专家
（引用数据：{{BIZ_DATA_REF}}）（引用新闻：{{BIZ_NEWS_REF}}）
{{EXPERT_BUSINESS_MD}}
→ 今日行动：{{ACTION_BUSINESS}}

### 🧬 学术科学专家
（引用数据：{{SCI_DATA_REF}}）（引用新闻：{{SCI_NEWS_REF}}）
{{EXPERT_SCIENCE_MD}}
→ 今日行动：{{ACTION_SCIENCE}}

### 🧠 心理健康专家
（引用数据：{{HEALTH_DATA_REF}}）（引用新闻：{{HEALTH_NEWS_REF}}）
{{EXPERT_HEALTH_MD}}
→ 今日行动：{{ACTION_HEALTH}}

### 🌐 综合专家
{{EXPERT_SYNTHESIS_MD}}
→ **明日第一行动**：明天{{TOMORROW_TIME}}，{{TOMORROW_ACTION}}，预计{{TOMORROW_DURATION}}，目标：{{TOMORROW_GOAL}}

## 🔮 知识节点

{{OBSIDIAN_TAGS}}
```

### Step 6b · HTML 文件（必须遵守的规则）

**文件名**：`daily_YYYY-MM-DD.html`

1. **完整使用 `references/html_template.md` 的 HTML 骨架**，不得删减任何 section 或 tab
2. **七个 Tab 必须全部存在**：概览 / 时间线 / 洞察&技能 / 成长轨迹 / 专家委员会 / 明日行动
3. **所有 CSS 必须内联**，不依赖外部文件（Google Fonts CDN 除外）
4. **概览页（#overview）必须包含**：
   - 活动分类卡片（终端/AI Agent/浏览器/应用）
   - 时间分布 SVG 图表（命令密度可视化）
   - AI 摘要卡片（`<div class="card">`）
5. **洞察&技能页（#insights）必须包含**：
   - 技能增强雷达模块（`.skill-module` + `.skill-item`）
   - 命令分类统计表
   - Obsidian 知识节点标签云
6. **能量曲线 SVG**：按规范生成（详见 html_template.md 的 SVG 规范）
7. **专家委员会**：五张卡片颜色/类名按下表：

| 专家 | CSS 类 | 背景 | 边框 |
|------|--------|------|------|
| 科技 | `.expert-card.tech` | `#f0fdf4` | `#4ade80` |
| 商业 | `.expert-card.business` | `#fefce8` | `#fde047` |
| 学术 | `.expert-card.science` | `#f0f9ff` | `#7dd3fc` |
| 健康 | `.expert-card.health` | `#fdf4ff` | `#d946ef` |
| 综合 | `.expert-card.synthesis` | `#1a1814` | `#c0392b` |

综合专家卡片：`grid-column: 1 / -1`，全宽深色背景，视觉压轴。

### Step 6c · 时间线条目类型样式

| 类型 | CSS 类 | 背景色 | 文字色 |
|------|--------|--------|--------|
| terminal | `.tl-tag.terminal` | `#d1fae5` | `#065f46` |
| agent | `.tl-tag.agent` | `#ede9fe` | `#5b21b6` |
| browser | `.tl-tag.browser` | `#dbeafe` | `#1e40af` |
| app / docker | `.tl-tag.app` | `#fef3c7` | `#92400e` |
| video | `.tl-tag.video` | `#fff7ed` | `#9a3412` |
| git | `.tl-tag.git` | `#dbeafe` | `#1e40af` |
| error | `.tl-tag.error` | `#fee2e2` | `#991b1b` |

### Step 6d · 技能增强条目 HTML 结构（必须遵守）

```html
<div class="skill-item">
  <span class="si-level basic">🔴 基础能力不足</span>
  <!-- 或：<span class="si-level advanced">🟡 进阶能力短板</span> -->
  <div><strong>技能名称</strong></div>
  <div style="margin:6px 0;font-size:.875rem">
    <strong>问题现象</strong>：[从日志中观察到的具体行为描述]
  </div>
  <div class="si-direction">
    立即解决：<br>
    · [具体命令 1]<br>
    · [具体命令 2]
  </div>
</div>
```

### Step 6e · Obsidian 知识节点（必须输出到 Markdown 和 HTML）

```markdown
## 🔮 知识节点

#{{项目名}} #{{技术栈}} #{{今日主要操作类型}}

[[{{涉及的主要项目}}]] · [[{{今日学到的技术概念}}]] · [[{{识别到的技能短板}}]]
```

HTML 版本（在 `#insights` section 内）：

```html
<div class="card" style="margin-top:20px">
  <h2>🔮 Obsidian 知识节点</h2>
  <div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:12px">
    <!-- 每个标签 -->
    <span style="background:#e0f2fe;color:#0369a1;padding:4px 10px;border-radius:20px;
                 font-size:.8rem;font-family:var(--font-mono)">#{{TAG}}</span>
    <!-- 双链节点 -->
    <span style="background:#f0fdf4;color:#166534;padding:4px 10px;border-radius:20px;
                 font-size:.8rem;border:1px solid #86efac">[[{{CONCEPT}}]]</span>
  </div>
</div>
```

### Step 6f · 文件输出路径

```
/mnt/user-data/outputs/
├── daily_YYYY-MM-DD.md
└── daily_YYYY-MM-DD.html
```

**两个文件全部生成完成后，必须调用 `present_files` 将两个文件一起提供给用户。**

---

## 周报模式

触发词：`生成周报` / `本周总结` / `weekly report`

### 数据来源

自动扫描过去7天日报（扫描路径同 Phase 3）：`daily_YYYY-MM-DD.md × 7份`

> **必须先阅读 `references/weekly_aggregator.md`**

### 周报 Markdown 结构（必须按顺序包含）

```markdown
# {{WEEK_RANGE}} 周报

> {{ONE_LINE_WEEK_SUMMARY}}

## 本周关键数字
| 指标 | 数值 |
|------|------|
| 有效工作天数 | |
| 总深度专注块 | |
| 总命令数 | |
| 项目推进数 | |

## 能量曲线对比（7天）
{{WEEK_ENERGY_DESC}}

## 项目进展汇总
{{PROJECT_WEEK_SUMMARY}}

## 技能成长矩阵
### 本周新出现的技能
### 持续强化的技能
### 重复出现的短板（需专项解决）

## 行为模式周分析
- 最高效的一天（数据支撑）：
- 最低效的一天（原因推断）：
- 娱乐/学习/开发时间占比：

## 本周新闻对个人的影响
{{WEEK_NEWS_IMPACT}}

## 专家委员会·周度版
### 🔬 科技专家（本周行业变化 × 技术演进）
### 💰 商业专家（本周市场信号 × 职业方向）
### 🧬 学术专家（本周科研突破 × 知识盲区）
### 🧠 健康专家（本周行为模式 × 身心趋势）
### 🌐 综合专家（下周最重要的一件事）

## 下周行动计划
1. [优先级最高]
2. [优先级次高]
3. ...（3-5条）

## 🔮 本周知识节点
{{WEEK_OBSIDIAN_TAGS}}
```

### 周报输出文件

```
/mnt/user-data/outputs/
├── weekly_YYYY-WNN.md
└── weekly_YYYY-WNN.html
```

数据不足时：标注"数据不足（N/7天），仅供参考"；缺失日标注 `[数据缺失]`。

---

## 技能增强模块规范

**每次生成日报时必须执行此模块。**

### 短板信号识别（按优先级）

```
1. 错误重试：同一问题出现 2+ 次错误 → 🔴 基础知识缺失
2. 绕道解决：复杂方式解决可简单完成的问题 → 🟡 进阶短板
3. 遗漏基础操作：事后发现更直接的命令 → 🔴 基础
4. 依赖复制粘贴不理解参数 → 🟡 进阶短板
5. 手动重复可自动化的操作 → 🟡 进阶短板
```

### 分级标准

```
🔴 基础能力不足
  判断：日常基本动作，正确做法只需 1~2 条命令
  输出：直接列出"立即解决"的具体命令 + 简短解释

🟡 进阶能力短板
  判断：方案能工作但不够优雅/安全/高效，需系统学习
  输出：列出 2~3 个具体学习方向（工具名/概念名/文档方向）
```

### 典型短板参考示例

| 信号 | 短板分类 | 级别 |
|------|---------|------|
| 每次 docker 都加 sudo | Docker 用户权限管理 | 🔴 基础 |
| apt 源配置错误反复尝试 | apt 源 & GPG 密钥 | 🔴 基础 |
| ssh 每次输密码 | ssh key-based auth | 🔴 基础 |
| 日志用 cat 查看 | journalctl/grep/less | 🔴 基础 |
| xhost + 完全开放 X11 | Docker X11/Wayland 安全 | 🟡 进阶 |
| git 冲突手动逐行解决 | git rebase/mergetool | 🟡 进阶 |
| 容器崩溃不会调试 | docker logs/exec/inspect | 🔴 基础 |

---

## 详细技术文档（阅读时机）

| 文档 | 阅读时机 | 说明 |
|------|---------|------|
| `references/html_template.md` | Phase 6 生成 HTML 前，**必须** | 完整 HTML 骨架、CSS、SVG 规范 |
| `references/news_sources.md` | Phase 4 抓取新闻前，**必须** | RSS Feed 源列表 + 完整抓取脚本 |
| `references/history_reader.md` | Phase 3 历史分析前，**必须** | 拐点算法、扫描路径 |
| `references/expert_prompts.md` | Phase 5 生成前，建议 | 完整专家提示词模板 |
| `references/weekly_aggregator.md` | 周报模式，**必须** | 周报聚合算法 |
| `scripts/collect.py` | Phase 1 执行 | 跨平台自动采集脚本 |

---

## 示例触发场景

- `生成今天的 lifelog` → 日报
- `帮我整理一下今天` → 日报
- `lifelog-pro` → 日报
- `生成周报` → 周报（聚合过去7天）
- `本周总结` → 周报
- `生成月报` → 月报（聚合过去30天）
- 粘贴 history 文本 + `做成日记` → 日报（合并手动输入）
- 上传视频截图 + `lifelog` → 日报（含视频解析）
