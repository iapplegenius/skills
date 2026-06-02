---
name: lifelog-pro
description: >
  超级个人成长日志系统 v3。主要为 Codex 和 Claude Code 两个 agent 工具设计，
  自动采集 AI 对话记录（Claude Code / Codex / Cursor / Hermes），结合 shell history、
  浏览器历史等生成日报/周报/月报。
  内置「专家委员会」模块：抓取 GitHub Trending / GitHub API / RSS 实时动态，
  五位专家对当日行业信号作出判断，若与用户当天行为有自然关联则带上，无关联不强行拼凑。
  重点是专家对当下的判断，而非复述用户行为。
  支持 Windows / macOS / Linux 全平台。
  触发词：生成日记、生成日报、生成周报、记录今天、lifelog、lifelog-pro、
  分析我今天、整理今天、日志、成长记录、周报、本周总结，
  以及所有原 lifelog-daily 触发词。
  即使用户只说「帮我整理一下今天」也应触发此 skill。
---

# LifeLog Pro v3 · 超级成长日志

> **⚠️ 首要规则：生成 HTML 前必须阅读 `references/html_template.md`；Phase 4 前必须阅读 `references/news_sources.md`。**

---

## 快速导航

| 阶段 | 说明 |
|------|------|
| Phase 0 | 判断模式（日/周/月） |
| Phase 1 | 采集数据（AI对话为主） |
| Phase 2 | 解析数据 |
| Phase 3 | 历史关联与拐点（读 `references/history_reader.md`）|
| Phase 4 | **抓取实时新闻**（读 `references/news_sources.md`）⭐ 核心 |
| Phase 5 | **专家委员会**（读 `references/expert_prompts.md`）⭐ 核心 |
| Phase 6 | 生成输出文件（读 `references/html_template.md`）|
| 周报模式 | 聚合7份日报（读 `references/weekly_aggregator.md`）|

---

## Phase 0 · 判断报告模式

| 用户说 | 模式 | 执行路径 |
|--------|------|---------|
| 日记/日报/今天/today | **日报** | Phase 1→6 |
| 周报/本周/this week | **周报** | [周报模式](#周报模式) |
| 月报/本月/this month | **月报** | 同周报逻辑，扫描30天 |

---

## Phase 1 · 采集数据

**规则：先运行自动采集脚本，再询问用户手动补充。**

```bash
python3 /tmp/lifelog-pro/scripts/collect.py
```

输出：`/tmp/lifelog-collect/collected_data.json`

### 数据源优先级（Codex / Claude Code 环境）

| 优先级 | 数据源 | 说明 |
|--------|--------|------|
| ⭐⭐⭐ 最高 | **Codex 对话记录** | 用户与 Codex agent 的完整对话 |
| ⭐⭐⭐ 最高 | **Claude Code 对话记录** | 用户与 Claude Code 的完整对话 |
| ⭐⭐ 高 | Shell history | bash/zsh/fish/PowerShell |
| ⭐⭐ 高 | 浏览器历史 | Chrome/Firefox/Edge/Safari |
| ⭐ 普通 | 软件/进程快照 | 工具使用时长 |
| ⭐ 普通 | 今日编辑文件 | 代码/文档变更 |

### Codex / Claude Code 对话日志路径（常见位置）

```
# Codex
~/.codex/logs/
~/.codex/conversations/
~/AppData/Roaming/Codex/logs/   (Windows)

# Claude Code
~/.claude/logs/
~/.claude/projects/*/conversations/
~/Library/Application Support/Claude/logs/   (macOS)

# Cursor
~/.cursor/logs/
~/.cursor/workspaceStorage/

# Hermes
~/.hermes/logs/
```

**失败自动跳过**，汇报成功/失败状态后继续。

---

## Phase 2 · 解析数据

### 2a · AI 对话解析（最高优先级）

从 Codex / Claude Code 等 agent 对话中提取：

```
- 会话总时长和轮次数
- 涉及的项目和任务（从对话内容推断）
- 关键成果（最终完成了什么）
- 卡点识别：同一问题被重复询问2次以上 → 知识盲区信号
- 使用的工具/命令（从对话中的代码块提取）
- 错误和修正次数
```

### 2b · Shell History 解析

- 命令分类：开发/运维/文件/网络/数据/AI工具/其他
- 提取项目名（从路径、git仓库名推断）
- 关键操作（git commit、pip install、创建文件）
- 错误与重试识别

**无时间戳时**：时间列填 `—`，标注 `no_timestamp`。

**有时间戳时额外提取**：
- 命令密度（每小时）→ 能量曲线
- 专注块（15分钟内无>5分钟中断）
- 错误恢复速度

### 2c · 浏览器历史解析

- 分类：技术文档/AI工具/社交/视频/购物/新闻/其他
- 提取搜索关键词（`q=` 参数）
- 重复搜索 → 知识盲区信号
- **隐私过滤**：银行/支付/登录 → `[已隐去]`

### 全局隐私过滤

含 `password/secret/token/key/api_key` 的内容 → `[已隐去敏感内容]`

---

## Phase 3 · 历史关联与拐点

> **必须先阅读 `references/history_reader.md`**

扫描路径：
```
1. /mnt/user-data/outputs/daily_*.md
2. ~/lifelog/daily_*.md
3. ~/Documents/lifelog/daily_*.md
4. ~/Desktop/lifelog/daily_*.md
5. ./daily_*.md
```

拐点识别（必须输出具体数据，禁止泛泛而谈）：

| 场景 | 判断 | 输出格式 |
|------|------|---------|
| 专注度下滑 | 今天比前3天均值低30% | "你的专注度从[日期]开始下滑" |
| 项目停滞 | >7天 | "停滞警告" |
| 短板复现 | 历史3次以上 | "持续短板，建议专项解决" |
| 正向连续 | 连续N天专注 | "你已连续N天保持深度工作" |

---

## Phase 4 · 实时新闻抓取

> **⚠️ 必须先阅读 `references/news_sources.md`**

### 执行顺序（Codex / Claude Code 环境）

**步骤1（必执行）**：GitHub Trending 解析

```bash
python3 - << 'PYEOF'
import urllib.request, re, json

url = 'https://github.com/trending?since=daily'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
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
            'repo': name.group(1).strip(),
            'desc': desc.group(1).strip()[:120] if desc else '',
            'lang': lang_.group(1).strip() if lang_ else '',
            'stars_today': stars.group(1) if stars else '?',
        })
print(json.dumps(results, ensure_ascii=False, indent=2))
PYEOF
```

**步骤2（必执行）**：GitHub API 近期 AI 热门项目  
（完整脚本见 `references/news_sources.md` 策略A2）

**步骤3（可选）**：RSS Feed 补充（科学/健康/财经）  
（源列表和脚本见 `references/news_sources.md` 策略C）

**步骤4（降级）**：若步骤1-3全部失败，使用 `web_search` 工具  
（搜索词见 `references/news_sources.md` 策略B）

### Claude.ai 环境

直接使用 `web_search` 工具，每类各执行1次搜索（见 `references/news_sources.md` 策略B）。

---

## Phase 5 · 专家委员会

> **必须先阅读 `references/expert_prompts.md` 获取完整提示词**

### ⚠️ 核心逻辑（与旧版不同）

```
新逻辑：
  新闻/GitHub Trending → 专家判断当下 → 若与用户行为自然关联则带上 → 输出建议

旧逻辑（禁止）：
  收集用户行为 → 强行找新闻关联 → 硬凑建议
```

### 五位专家角色

| 专家 | 核心信息来源 | 用户数据的使用条件 |
|------|------------|-----------------|
| 🔬 科技 | GitHub Trending + 科技新闻 | 有自然关联时引用 |
| 💰 商业 | 财经新闻 + GitHub商业信号 | 有自然关联时引用 |
| 🧬 学术 | arxiv + 科研新闻 + 前沿repo | 有自然关联时引用 |
| 🧠 健康 | 健康新闻（主）/ 用户行为数据（健康新闻缺失时） | **此专家例外**：无健康新闻时以用户行为为主 |
| 🌐 综合 | 以上四位全部输出 + 全量新闻 | 串联信号，给出明日行动 |

### 强制质量规则

1. **每位专家的论点必须引用具体新闻标题或repo名**（不能用「行业趋势」代替）
2. **新闻获取失败时必须标注**：`（{类别}新闻今日未获取，以下为行业背景判断）`
3. **每位专家给出一个具体可执行行动**：格式「用X工具做Y，预计Z分钟」
4. **综合专家给出明日第一行动**：「明天[时间]，做[具体事]，预计[时长]，目标：[可验证结果]」
5. **字数**：每位正文 4-6 句；综合专家 6-8 句
6. **零容忍**：「你很棒」「继续加油」「保持学习」等空话一律不输出

---

## Phase 6 · 生成输出文件

> **⚠️ 生成 HTML 前必须阅读 `references/html_template.md`**

### Step 6a · Markdown 文件（`daily_YYYY-MM-DD.md`）

```markdown
---
date: {{DATE}}
generated_at: {{DATETIME}}
tags: [{{TAG_LIST}}]
data_sources: [{{SOURCES}}]
news_sources: [{{NEWS_SOURCES}}]
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
### AI Agent 对话摘要
{{AGENT_CONVERSATION_SUMMARY}}

### 涉及项目
{{PROJECT_LIST}}

### 关键成果
{{KEY_OUTPUTS}}

### 卡点记录（知识盲区）
{{STICKING_POINTS}}

### 命令分类统计
| 类别 | 数量 | 占比 |
|------|------|------|
{{CMD_STATS}}

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

> 信息来源：{{NEWS_SOURCES_USED}}

### 🔬 科技专家
（新闻来源：{{TECH_NEWS_REF}}）
{{EXPERT_TECH_MD}}
→ 今日行动：{{ACTION_TECH}}

### 💰 商业投资专家
（新闻来源：{{BIZ_NEWS_REF}}）
{{EXPERT_BUSINESS_MD}}
→ 今日行动：{{ACTION_BUSINESS}}

### 🧬 学术科学专家
（新闻来源：{{SCI_NEWS_REF}}）
{{EXPERT_SCIENCE_MD}}
→ 今日行动：{{ACTION_SCIENCE}}

### 🧠 心理健康专家
（{{HEALTH_SOURCE_NOTE}}）
{{EXPERT_HEALTH_MD}}
→ 今日行动：{{ACTION_HEALTH}}

### 🌐 综合专家
{{EXPERT_SYNTHESIS_MD}}
→ **明日第一行动**：明天{{TOMORROW_TIME}}，{{TOMORROW_ACTION}}，预计{{TOMORROW_DURATION}}，目标：{{TOMORROW_GOAL}}

## 🔮 知识节点
{{OBSIDIAN_TAGS}}
```

### Step 6b · HTML 文件（`daily_YYYY-MM-DD.html`）

严格遵守 `references/html_template.md` 的完整骨架，**不得自行简化**。

必须包含的 Tab（共六个）：概览 / 时间线 / AI对话摘要 / 洞察&技能 / 成长轨迹 / 专家委员会

专家卡片 CSS 规范：

| 专家 | CSS 类 | 背景 | 边框 |
|------|--------|------|------|
| 科技 | `.expert-card.tech` | `#f0fdf4` | `#4ade80` |
| 商业 | `.expert-card.business` | `#fefce8` | `#fde047` |
| 学术 | `.expert-card.science` | `#f0f9ff` | `#7dd3fc` |
| 健康 | `.expert-card.health` | `#fdf4ff` | `#d946ef` |
| 综合 | `.expert-card.synthesis` | `#1a1814` | `#c0392b` |

综合专家卡片：`grid-column: 1 / -1`，全宽深色背景，视觉压轴。

### Step 6c · 时间线条目类型

| 类型 | CSS 类 | 含义 |
|------|--------|------|
| agent | `.tl-tag.agent` | Codex/Claude Code 对话 |
| terminal | `.tl-tag.terminal` | Shell 命令 |
| browser | `.tl-tag.browser` | 浏览器访问 |
| app | `.tl-tag.app` | 应用/工具使用 |
| git | `.tl-tag.git` | Git 操作 |
| error | `.tl-tag.error` | 错误/失败 |

### Step 6d · 文件输出路径

```
/mnt/user-data/outputs/
├── daily_YYYY-MM-DD.md
└── daily_YYYY-MM-DD.html
```

**两个文件全部生成完成后，必须调用 `present_files` 将两个文件一起提供给用户。**

---

## 技能增强模块

**每次生成日报时必须执行**（从 AI 对话和 Shell History 中识别）：

### 短板信号识别

```
1. AI对话中同一问题被问2次以上 → 🔴 知识盲区
2. Shell命令中同类错误重试2次 → 🔴 基础知识缺失
3. 复杂方式解决可简单完成的问题 → 🟡 进阶短板
4. 从对话记录看出依赖AI解释但不理解原理 → 🟡 进阶短板
5. 手动重复可自动化的操作 → 🟡 进阶短板
```

### HTML 结构

```html
<div class="skill-item">
  <span class="si-level basic">🔴 基础能力不足</span>
  <div><strong>技能名称</strong></div>
  <div style="margin:6px 0;font-size:.875rem">
    <strong>问题现象</strong>：[从日志中观察到的具体行为]
  </div>
  <div class="si-direction">
    立即解决：<br>
    · [具体命令/文档 1]<br>
    · [具体命令/文档 2]
  </div>
</div>
```

---

## 周报模式

> **必须先阅读 `references/weekly_aggregator.md`**

触发词：`生成周报` / `本周总结` / `weekly report`

自动扫描过去7天日报（扫描路径同 Phase 3）。

周报结构同旧版，专家委员会部分遵循同样的「新闻为主，行为为辅」原则。

输出文件：
```
/mnt/user-data/outputs/
├── weekly_YYYY-WNN.md
└── weekly_YYYY-WNN.html
```

---

## 详细技术文档（阅读时机）

| 文档 | 何时阅读 | 内容 |
|------|---------|------|
| `references/html_template.md` | Phase 6 生成 HTML **之前**，必须 | 完整骨架、CSS、SVG 规范 |
| `references/news_sources.md` | Phase 4 抓取新闻**之前**，必须 | GitHub Trending/API 脚本、RSS 源、降级策略 |
| `references/history_reader.md` | Phase 3 历史分析前，必须 | 拐点算法、扫描路径 |
| `references/expert_prompts.md` | Phase 5 生成前，必须 | 完整专家提示词和逻辑规则 |
| `references/weekly_aggregator.md` | 周报模式，必须 | 周报聚合算法 |
| `scripts/collect.py` | Phase 1 执行 | 跨平台自动采集脚本 |

---

## 触发场景示例

- `生成今天的 lifelog` → 日报
- `帮我整理一下今天` → 日报
- `lifelog-pro` → 日报
- `生成周报` → 周报（聚合过去7天）
- `本周总结` → 周报
- 粘贴 Codex 对话记录 + `做成日记` → 日报（合并手动输入）
- 粘贴 Claude Code 会话 + `lifelog` → 日报

---

## Codex / Claude Code 兼容性说明

此 skill 被 Codex 或 Claude Code 调用时：

1. **工具权限**：Phase 4 的 Python 脚本需要网络权限（执行前确认）
2. **文件路径**：输出路径 `/mnt/user-data/outputs/` 如不存在，改用 `~/lifelog/` 或当前目录
3. **API调用**：专家委员会可通过 Anthropic API 调用生成（见 `references/expert_prompts.md`），或在主会话中直接生成
4. **无交互模式**：若在非交互环境中运行，跳过「向用户汇报」步骤，直接生成文件
