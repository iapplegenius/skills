---
name: lifelog-daily
description: >
  根据用户提供的终端 history 文本和/或视频截图，自动生成当天的个人日志，
  输出详细的 Markdown 文件（daily_YYYY-MM-DD.md）和可视化美观的 HTML 日报
  （daily_YYYY-MM-DD.html）。
  当用户提到"生成日记"、"生成日报"、"记录今天"、"分析我的 history"、
  "把今天的操作整理成日志"、"lifelog"、上传了截图或粘贴了命令历史并希望整理，
  或提供 shell history / 视频截图并希望输出日志/日记/报告时，必须使用此 skill。
  即使用户只说"帮我整理一下今天"也应触发。
---

# LifeLog Daily · Skill

将终端 history + 视频截图 → 精美个人日志（.md + .html）

---

## 输入类型

| 输入 | 格式 | 说明 |
|------|------|------|
| 终端历史 | 纯文本（粘贴或文件） | `history` 命令输出，或 `.bash_history` / `.zsh_history` 文件内容 |
| 视频截图 | 图片（PNG/JPG） | 截图来自视频播放器、B站、YouTube等，用于识别今天看了什么视频 |

两种输入可以同时提供，也可以只提供其中一种。

---

## 处理流程

### Step 1 · 解析终端 History

对 history 文本进行分析，提取以下信息：

```
1. 时间信息
   - 如果 history 带时间戳（扩展格式）：直接提取
   - 如果没有时间戳：根据命令顺序推断相对时序，标注"时间未知"

2. 命令分类（按以下类别归类）
   - 项目开发：git, npm, pip, python, node, make, cargo, go 等
   - 系统运维：docker, kubectl, ssh, systemctl, ps, top 等
   - 文件操作：cd, ls, cp, mv, rm, mkdir, find, cat, vim 等
   - 网络调试：curl, wget, ping, nslookup, nc 等
   - 数据处理：grep, awk, sed, jq, sort, cut 等
   - 其他

3. 提取关键信息
   - 主要工作项目（从路径、git仓库名、pip包名推断）
   - 关键操作（git commit消息、安装的包、创建的文件）
   - 错误与重试（连续的失败命令）
   - 工作节奏（命令密集/稀疏区间）
```

### Step 2 · 解析视频截图（如有）

对每张图片进行视觉识别：

```
1. 识别视频平台（B站、YouTube、Netflix、本地播放器等）
2. 提取视频标题（如可见）
3. 识别播放进度/时长（如可见）
4. 判断内容类别（技术教程、娱乐、纪录片、会议录屏等）
5. 记录截图中的关键画面信息
```

### Step 3 · 构建时间线与日报结构

整合所有信息，构建如下结构：

```
日报结构：
├── 元信息（日期、生成时间、数据来源）
├── 今日概览（总结性文字，AI生成）
├── 时间线（按时间顺序的事件列表）
├── 工作/开发摘要
│   ├── 涉及的项目
│   ├── 主要操作
│   └── 命令统计
├── 视频/学习记录（如有截图）
├── 今日成就与待续
├── 技能增强雷达（见 Step 4b）
└── 知识节点标签（供 Obsidian 使用）
```

### Step 4 · 生成两种输出文件

#### 4a · Markdown 文件（详细版）

文件名：`daily_YYYY-MM-DD.md`

遵循以下模板（见下方 MARKDOWN TEMPLATE）：
- YAML frontmatter 包含 tags、date 等 Obsidian 兼容字段
- 完整时间线表格
- 命令分类统计
- AI 生成的叙事摘要
- Obsidian 双链标签

#### 4b · HTML 文件（可读版）

文件名：`daily_YYYY-MM-DD.html`

遵循以下设计规范（见下方 HTML DESIGN SPEC）：
- 单文件，内联所有 CSS/JS，无外部依赖（字体可用 Google Fonts CDN）
- **四个 Tab：概览 / 时间线 / 洞察 & 技能增强**
- 时间分布可视化（SVG 图表）
- AI 摘要卡片
- 命令记录时间线
- **技能增强雷达模块**（见下方 SKILL ENHANCEMENT MODULE）

---

## Markdown 模板

```markdown
---
date: {{DATE}}
generated_at: {{DATETIME}}
tags: [{{TAG_LIST}}]
data_sources: [{{SOURCES}}]
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

{{SKILL_ITEMS}}

## 知识节点

{{OBSIDIAN_TAGS}}
```

---

## HTML 设计规范

### 视觉风格
- **配色**：深墨色背景 header（`#1a1814`）+ 暖米色纸质正文背景（`#f7f4ef`）
- **字体**：
  - 标题：`Noto Serif SC`（中文衬线）
  - 正文：`Noto Sans SC`（中文无衬线）  
  - 代码/数字：`JetBrains Mono`
- **强调色**：`#c0392b`（红）做点缀，`#1d3557`（深蓝）做工作类，`#2d6a4f`（深绿）做学习类
- **技能模块**：渐变背景 `#fff0f3 → #fdf2ff`，粉红边框 `#f9a8d4`

### 结构
```html
<header>   <!-- 深色，显示日期、关键数字统计 -->
<nav.tabs> <!-- 概览 / 时间线 / 洞察&技能，sticky -->
<main>
  <section#overview>  <!-- 分类卡片 + 时间分布图 + AI摘要 -->
  <section#timeline>  <!-- 命令时间线，带类型标签 -->
  <section#insights>  <!-- 技能增强雷达 + 命令统计 + Obsidian标签 -->
</main>
<footer>   <!-- "ALL DATA LOCAL · NEVER UPLOADED" -->
```

### 时间线条目类型与配色
| 类型 | tag 文字 | 背景色 | 文字色 |
|------|---------|--------|--------|
| terminal | TERMINAL | `#d1fae5` | `#065f46` |
| video | VIDEO | `#fff7ed` | `#9a3412` |
| git | GIT | `#dbeafe` | `#1e40af` |
| error | ERROR | `#fee2e2` | `#991b1b` |
| docker | DOCKER | `#ede9fe` | `#5b21b6` |
| dev | DEV | `#fef3c7` | `#92400e` |

---

## 技能增强模块（SKILL ENHANCEMENT MODULE）

这是本 skill 的核心扩展功能。**每次生成日报时必须执行此模块**，从当天的操作过程中识别技能短板，输出到 HTML 的"洞察 & 技能增强"Tab 和 Markdown 的"技能增强雷达"章节。

### 诊断规则

分析操作日志时，重点关注以下信号：

```
短板信号识别（按优先级）：
1. 错误重试：同一问题出现 2+ 次错误 → 基础知识缺失
2. 绕道解决：用复杂方式解决本可简单完成的问题
3. 遗漏基础操作：完成任务后才发现有更直接的命令/方法
4. 依赖他人方案：直接复制命令但不理解参数含义
5. 效率低下：手动重复做可以自动化的操作
```

### 短板分级标准

```
🔴 基础能力不足（直接给出命令/解释）
   判断依据：
   - 该操作是日常运维/开发的基本动作
   - 正确做法只需 1~2 条命令
   - 错误源于不了解工具的基本用法
   输出要求：直接列出"立即解决"的具体命令，并附简短解释

🟡 进阶能力短板（给出学习方向）
   判断依据：
   - 当前方案能工作但不够优雅/安全/高效
   - 最佳实践需要系统学习才能掌握
   - 涉及架构设计、性能优化、安全加固等
   输出要求：列出 2~3 个具体学习方向，指向工具名/概念名/文档方向
```

### 每条技能条目的结构

```markdown
### [🔴/🟡] 技能名称

**问题现象**：从日志中观察到的具体行为描述

**[立即解决 / 学习方向]**：
- 具体命令或学习方向 1
- 具体命令或学习方向 2
- ...
```

### HTML 技能模块样式规范

```css
/* 技能模块容器 */
.skill-module {
  background: linear-gradient(135deg, #fff0f3 0%, #fdf2ff 100%);
  border: 1.5px solid #f9a8d4;
  border-radius: 12px;
  padding: 24px 26px;
}

/* 技能条目 */
.skill-item {
  background: white;
  border: 1px solid #fce7f3;
  border-radius: 8px;
  padding: 16px 18px;
  margin-bottom: 12px;
}

/* 级别徽章 */
.si-level.basic    { background: #fee2e2; color: #991b1b; }  /* 🔴 基础 */
.si-level.advanced { background: #fef3c7; color: #92400e; }  /* 🟡 进阶 */

/* 学习方向框 */
.si-direction {
  color: #6d28d9;
  background: #ede9fe;
  border-radius: 5px;
  padding: 8px 12px;
}
```

### 典型技能短板示例库

以下是常见短板及标准诊断输出，可直接参考：

| 信号 | 短板分类 | 级别 |
|------|---------|------|
| 每次 docker 都加 sudo | Docker 用户权限管理 | 🔴 基础 |
| apt 源配置错误反复尝试 | apt 源 & GPG 密钥 | 🔴 基础 |
| deb 包 postinst 报错不知如何绕过 | dpkg 包结构 | 🔴 基础 |
| xhost + 完全开放 X11 | Docker X11/Wayland 安全 | 🟡 进阶 |
| 暴力破解速度极慢 | hashcat/专业密码工具 | 🟡 进阶 |
| git 冲突手动逐行解决 | git rebase/mergetool | 🟡 进阶 |
| vim 多文件编辑低效 | vim 进阶操作 | 🔴 基础 |
| ssh 每次输密码 | ssh key-based auth | 🔴 基础 |
| 日志用 cat 查看 | journalctl/grep/less | 🔴 基础 |
| 容器崩溃不会调试 | docker logs/exec/inspect | 🔴 基础 |

---

## 关键实现细节

### 处理无时间戳的 history

大多数 `history` 输出格式为：
```
  123  git status
  124  git add .
  125  git commit -m "feat: add collector"
```

此时：
- 无法推断具体时间，时间列填写 `—`
- 在 frontmatter 中标注 `data_sources: [terminal_history_no_timestamp]`
- 在报告开头说明"命令时间信息不可用，以顺序展示"

如果是带时间戳格式（`HISTTIMEFORMAT` 已设置）：
```
  123  2025-05-13 09:32:15 git status
```
则正常提取时间。

### 命令过滤与隐私

以下命令类型在生成报告时**隐去完整参数**，只保留命令名：
- 包含 `password`、`passwd`、`secret`、`token`、`key`、`api_key` 的命令
- `export` 命令（可能包含环境变量密钥）
- `curl` / `wget` 带 `-H "Authorization` 的命令

显示为：`curl [已隐去敏感参数]`

### 视频截图处理

- 如果截图中无法识别标题，记录为"视频内容（标题未识别）"并附上图片描述
- 如果有多张截图来自同一视频，合并为一条记录
- 截图中的弹幕/字幕信息也可作为内容线索

---

## 文件输出

两个文件均输出到 `/mnt/user-data/outputs/`：

```
/mnt/user-data/outputs/
├── daily_YYYY-MM-DD.md
└── daily_YYYY-MM-DD.html
```

生成完成后使用 `present_files` 将两个文件一起提供给用户。

---

## 示例触发场景

- 用户粘贴一大段命令历史："帮我整理成今天的日记"
- 用户上传几张视频截图 + 粘贴 history："生成今天的 lifelog"
- 用户说："把我今天的终端操作做成日报"
- 用户上传 `.zsh_history` 文件
- 用户说："分析我今天做了什么，输出 md 和 html"
