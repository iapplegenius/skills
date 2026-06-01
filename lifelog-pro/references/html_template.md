# LifeLog Pro · HTML 模板规范 v2

## 六 Tab 结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{DATE}} · LifeLog Pro</title>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700&family=Noto+Sans+SC:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-header: #1a1814; --bg-body: #f7f4ef; --bg-card: #ffffff;
      --accent-red: #c0392b; --accent-blue: #1d3557; --accent-green: #2d6a4f;
      --text-primary: #1a1814; --text-secondary: #6b7280; --border: #e5e0d8;
      --font-serif: 'Noto Serif SC', serif;
      --font-sans: 'Noto Sans SC', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: var(--font-sans); background: var(--bg-body); color: var(--text-primary); }

    /* Header */
    header { background: var(--bg-header); color: #f7f4ef; padding: 32px 40px; }
    header h1 { font-family: var(--font-serif); font-size: 2rem; margin-bottom: 8px; }
    .subtitle { color: #a09890; font-size: 0.9rem; margin-bottom: 20px; }
    .header-stats { display: flex; gap: 16px; flex-wrap: wrap; }
    .stat-item { background: rgba(255,255,255,0.08); border-radius: 8px; padding: 10px 16px; text-align: center; }
    .stat-num { font-family: var(--font-mono); font-size: 1.4rem; color: #f7f4ef; }
    .stat-label { font-size: 0.7rem; color: #a09890; }

    /* Nav */
    nav.tabs { background: var(--bg-header); border-bottom: 1px solid #2a2520;
      position: sticky; top: 0; z-index: 100; display: flex; padding: 0 40px; overflow-x: auto; }
    nav.tabs button { background: none; border: none; color: #a09890; padding: 14px 18px;
      cursor: pointer; font-family: var(--font-sans); font-size: 0.85rem;
      border-bottom: 3px solid transparent; white-space: nowrap; transition: all 0.2s; }
    nav.tabs button.active, nav.tabs button:hover { color: #f7f4ef; border-bottom-color: var(--accent-red); }

    /* Main */
    main { max-width: 1100px; margin: 0 auto; padding: 32px 40px; }
    section { display: none; }
    section.active { display: block; }

    /* Cards */
    .card { background: var(--bg-card); border: 1px solid var(--border);
      border-radius: 12px; padding: 24px; margin-bottom: 20px; }
    .card h2 { font-family: var(--font-serif); font-size: 1.15rem; margin-bottom: 16px;
      border-bottom: 2px solid var(--border); padding-bottom: 10px; }

    /* Energy Curve */
    .energy-chart { width: 100%; height: 160px; }
    .energy-wrap { background: #fafafa; border: 1px solid var(--border); border-radius: 10px;
      padding: 16px; margin-bottom: 20px; }

    /* Timeline */
    .tl-item { display: flex; gap: 14px; padding: 11px 0; border-bottom: 1px solid var(--border); align-items: flex-start; }
    .tl-time { font-family: var(--font-mono); font-size: 0.78rem; color: var(--text-secondary); min-width: 55px; padding-top: 2px; }
    .tl-tag { font-size: 0.62rem; font-weight: 700; padding: 2px 7px; border-radius: 4px; white-space: nowrap; }
    .tl-tag.terminal { background:#d1fae5;color:#065f46; }
    .tl-tag.agent    { background:#ede9fe;color:#5b21b6; }
    .tl-tag.browser  { background:#dbeafe;color:#1e40af; }
    .tl-tag.app      { background:#fef3c7;color:#92400e; }
    .tl-tag.video    { background:#fff7ed;color:#9a3412; }
    .tl-tag.git      { background:#dbeafe;color:#1e40af; }
    .tl-tag.error    { background:#fee2e2;color:#991b1b; }
    .tl-content { font-size: 0.875rem; line-height: 1.6; }

    /* Skills */
    .skill-module { background: linear-gradient(135deg, #fff0f3, #fdf2ff);
      border: 1.5px solid #f9a8d4; border-radius: 12px; padding: 24px; margin-bottom: 20px; }
    .skill-item { background: white; border: 1px solid #fce7f3; border-radius: 8px;
      padding: 16px; margin-bottom: 12px; }
    .si-level { display: inline-block; font-size: 0.68rem; font-weight: 700;
      padding: 2px 8px; border-radius: 4px; margin-bottom: 8px; }
    .si-level.basic    { background:#fee2e2;color:#991b1b; }
    .si-level.advanced { background:#fef3c7;color:#92400e; }
    .si-direction { color:#6d28d9;background:#ede9fe;border-radius:5px;padding:8px 12px;font-size:0.85rem;margin-top:8px; }

    /* Growth */
    .growth-card { background: linear-gradient(135deg,#f0f9ff,#e0f2fe);
      border: 1.5px solid #7dd3fc; border-radius: 12px; padding: 24px; margin-bottom: 20px; }
    .turning-point { background:#fffbeb;border-left:4px solid #f59e0b;padding:12px 16px;border-radius:0 8px 8px 0;margin:10px 0;font-size:0.875rem; }
    .three-dim { display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-top:20px; }
    .dim-card { background:white;border-radius:10px;padding:18px;border:1px solid var(--border); }
    .dim-card h3 { font-size:0.875rem;font-weight:700;margin-bottom:10px; }
    .dim-card.psych h3 { color:#0369a1; }
    .dim-card.behavior h3 { color:#065f46; }
    .dim-card.skill h3 { color:#7c3aed; }

    /* Expert Committee */
    .expert-grid { display:grid;grid-template-columns:1fr 1fr;gap:20px; }
    .expert-card { border-radius:14px;padding:22px 24px;position:relative; }
    .expert-card.tech       { background:#f0fdf4;border:1.5px solid #4ade80; }
    .expert-card.business   { background:#fefce8;border:1.5px solid #fde047; }
    .expert-card.science    { background:#f0f9ff;border:1.5px solid #7dd3fc; }
    .expert-card.health     { background:#fdf4ff;border:1.5px solid #d946ef; }
    .expert-card.synthesis  { grid-column:1/-1;background:var(--bg-header);color:#f7f4ef;
      border:2px solid var(--accent-red); }

    .expert-icon { font-size:1.8rem;margin-bottom:8px; }
    .expert-title { font-family:var(--font-serif);font-size:0.95rem;font-weight:700;margin-bottom:2px; }
    .expert-role { font-size:0.72rem;color:var(--text-secondary);margin-bottom:12px; }
    .expert-card.synthesis .expert-role { color:#a09890; }
    .news-ref { font-size:0.68rem;color:#9ca3af;background:rgba(0,0,0,0.04);
      border-radius:4px;padding:3px 8px;margin-bottom:12px;display:inline-block; }
    .expert-card.synthesis .news-ref { background:rgba(255,255,255,0.08);color:#a09890; }
    .expert-text { font-size:0.875rem;line-height:1.85;color:#374151; }
    .expert-card.synthesis .expert-text { color:#e5e0d8; }
    .expert-action { margin-top:14px;padding:10px 14px;background:rgba(0,0,0,0.04);
      border-radius:6px;font-size:0.8rem;font-weight:600; }
    .expert-card.synthesis .expert-action { background:rgba(192,57,43,0.15);color:#f87171; }
    .action-label { font-size:0.65rem;font-weight:700;letter-spacing:.05em;
      color:var(--text-secondary);margin-bottom:3px; }
    .expert-card.synthesis .action-label { color:#a09890; }

    /* Tomorrow Tab */
    .tomorrow-hero { background:var(--bg-header);color:#f7f4ef;border-radius:14px;
      padding:32px;margin-bottom:24px;text-align:center; }
    .tomorrow-hero h2 { font-family:var(--font-serif);font-size:1.5rem;margin-bottom:8px; }
    .tomorrow-action { font-size:1rem;color:#f9a8d4;margin-top:16px;line-height:1.8; }
    .priority-list { list-style:none; }
    .priority-list li { background:white;border:1px solid var(--border);border-radius:10px;
      padding:16px 20px;margin-bottom:12px;display:flex;gap:16px;align-items:flex-start; }
    .priority-num { font-family:var(--font-mono);font-size:1.2rem;font-weight:700;
      color:var(--accent-red);min-width:28px; }

    /* Footer */
    footer { text-align:center;padding:24px;color:var(--text-secondary);
      font-size:0.72rem;font-family:var(--font-mono);
      border-top:1px solid var(--border);margin-top:40px; }

    @media(max-width:768px){
      main{padding:16px;}
      .expert-grid,.three-dim{grid-template-columns:1fr;}
      .expert-card.synthesis{grid-column:auto;}
      nav.tabs{padding:0 16px;}
    }
  </style>
</head>
<body>

<header>
  <h1>{{DATE}} · LifeLog Pro</h1>
  <div class="subtitle">{{ONE_LINE_SUMMARY}}</div>
  <div class="header-stats">
    <div class="stat-item"><div class="stat-num">{{CMD_COUNT}}</div><div class="stat-label">终端命令</div></div>
    <div class="stat-item"><div class="stat-num">{{FOCUS_BLOCKS}}</div><div class="stat-label">专注块</div></div>
    <div class="stat-item"><div class="stat-num">{{BROWSER_VISITS}}</div><div class="stat-label">浏览器访问</div></div>
    <div class="stat-item"><div class="stat-num">{{AGENT_SESSIONS}}</div><div class="stat-label">AI Agent会话</div></div>
    <div class="stat-item"><div class="stat-num">{{HISTORY_DAYS}}天</div><div class="stat-label">历史关联</div></div>
    <div class="stat-item"><div class="stat-num">{{DATA_SOURCES}}</div><div class="stat-label">数据源</div></div>
  </div>
</header>

<nav class="tabs">
  <button class="active" onclick="showTab('overview',this)">🏠 概览</button>
  <button onclick="showTab('timeline',this)">📋 时间线</button>
  <button onclick="showTab('growth',this)">📈 成长轨迹</button>
  <button onclick="showTab('skills',this)">🎯 技能增强</button>
  <button onclick="showTab('experts',this)">🧠 专家委员会</button>
  <button onclick="showTab('tomorrow',this)">🚀 明日行动</button>
</nav>

<main>
  <section id="overview" class="active">
    <div class="energy-wrap">
      <h3 style="font-size:.85rem;font-weight:700;margin-bottom:12px;color:var(--text-secondary)">TODAY'S ENERGY CURVE</h3>
      <svg class="energy-chart" viewBox="0 0 800 160" xmlns="http://www.w3.org/2000/svg">
        <!-- X轴：0-24小时 -->
        {{ENERGY_CURVE_SVG}}
      </svg>
    </div>
    <div class="card"><h2>今日概览</h2><p>{{AI_NARRATIVE}}</p></div>
    {{OVERVIEW_CARDS}}
  </section>

  <section id="timeline">
    <div class="card">
      <h2>全数据源合并时间线</h2>
      {{TIMELINE_HTML}}
    </div>
  </section>

  <section id="growth">
    <div class="growth-card">
      <h2>📈 成长轨迹（关联过去 {{HISTORY_DAYS}} 天）</h2>
      {{GROWTH_NARRATIVE}}
      {{TURNING_POINTS_HTML}}
    </div>
    <div class="card">
      <h2>🧠 三维分析</h2>
      <div class="three-dim">
        <div class="dim-card psych"><h3>🧠 心理状态</h3>{{PSYCH}}</div>
        <div class="dim-card behavior"><h3>⚡ 行为模式</h3>{{BEHAVIOR}}</div>
        <div class="dim-card skill"><h3>🎯 技能成长</h3>{{SKILL_GROWTH}}</div>
      </div>
    </div>
  </section>

  <section id="skills">
    <div class="skill-module">
      <h2>🎯 技能增强雷达</h2>
      {{SKILL_ITEMS_HTML}}
    </div>
  </section>

  <section id="experts">
    <div class="expert-grid">
      <div class="expert-card tech">
        <div class="expert-icon">🔬</div>
        <div class="expert-title">科技领域专家</div>
        <div class="expert-role">顶级 LLM · 硅谷工程师 · AI研究员视角</div>
        <div class="news-ref">📰 {{TECH_NEWS_REF}}</div>
        <div class="expert-text">{{EXPERT_TECH}}</div>
        <div class="expert-action"><div class="action-label">→ 今日行动</div>{{ACTION_TECH}}</div>
      </div>

      <div class="expert-card business">
        <div class="expert-icon">💰</div>
        <div class="expert-title">商业/投资专家</div>
        <div class="expert-role">顶级 LLM · 一线投资人 · 产业分析师视角</div>
        <div class="news-ref">📰 {{FINANCE_NEWS_REF}}</div>
        <div class="expert-text">{{EXPERT_BUSINESS}}</div>
        <div class="expert-action"><div class="action-label">→ 今日行动</div>{{ACTION_BUSINESS}}</div>
      </div>

      <div class="expert-card science">
        <div class="expert-icon">🧬</div>
        <div class="expert-title">学术/科学专家</div>
        <div class="expert-role">顶级 LLM · 跨学科研究者 · 知识图谱视角</div>
        <div class="news-ref">📰 {{SCIENCE_NEWS_REF}}</div>
        <div class="expert-text">{{EXPERT_SCIENCE}}</div>
        <div class="expert-action"><div class="action-label">→ 今日行动</div>{{ACTION_SCIENCE}}</div>
      </div>

      <div class="expert-card health">
        <div class="expert-icon">🧠</div>
        <div class="expert-title">心理/健康专家</div>
        <div class="expert-role">顶级 LLM · 认知科学家 · 功能医学医生视角</div>
        <div class="news-ref">📰 {{HEALTH_NEWS_REF}}</div>
        <div class="expert-text">{{EXPERT_HEALTH}}</div>
        <div class="expert-action"><div class="action-label">→ 今日行动</div>{{ACTION_HEALTH}}</div>
      </div>

      <div class="expert-card synthesis">
        <div class="expert-icon">🌐</div>
        <div class="expert-title">综合专家</div>
        <div class="expert-role">整合四位专家 · 全量数据 · 全量新闻的超级视角</div>
        <div class="news-ref">综合以上所有信号</div>
        <div class="expert-text">{{EXPERT_SYNTHESIS}}</div>
        <div class="expert-action">
          <div class="action-label">🚀 明日第一行动</div>
          {{ACTION_TOMORROW}}
        </div>
      </div>
    </div>
  </section>

  <section id="tomorrow">
    <div class="tomorrow-hero">
      <h2>🚀 明日行动计划</h2>
      <p style="color:#a09890;font-size:.875rem">基于今日数据 + 专家委员会建议</p>
      <div class="tomorrow-action">{{TOMORROW_FIRST_ACTION}}</div>
    </div>
    <ul class="priority-list">
      {{PRIORITY_ITEMS}}
    </ul>
  </section>
</main>

<footer>ALL DATA LOCAL · PRIVACY FIRST · NEVER UPLOADED · LIFELOG PRO v2</footer>

<script>
function showTab(id, btn) {
  document.querySelectorAll('section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('nav.tabs button').forEach(b => b.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  if(btn) btn.classList.add('active');
}
</script>
</body>
</html>
```

## 能量曲线 SVG 生成规范

```
viewBox: 0 0 800 160
x轴范围: 0-24h → 映射到 x: 20-780
y轴范围: 0-1 → 映射到 y: 140-10（反转，越高越忙）

折线颜色：
  dev/terminal: #1d3557（蓝）
  browser: #f59e0b（橙）
  agent: #7c3aed（紫）
  idle/unknown: #d1d5db（灰）

专注块：
  矩形底纹，fill: rgba(45,106,79,0.08)，标注"专注"文字

X轴刻度：6、9、12、15、18、21（小时）
Y轴：不显示数字，仅做参考线
```

## 周报 HTML 补充

周报使用同样的 HTML 骨架，但 Tab 改为：
```
本周概览 / 能量对比图 / 项目矩阵 / 技能追踪 / 专家委员会·周度版
```

能量对比图：7条折线叠加，每天一个颜色，图例标注日期。

---

## 概览页（#overview）完整结构规范

概览页必须包含以下四个区块，**按顺序**输出：

### 区块1：活动分类卡片（`.overview-grid`）

```html
<div class="overview-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:20px">
  <!-- 终端活动卡片 -->
  <div class="ov-card" style="background:#f0fdf4;border:1.5px solid #86efac;border-radius:12px;padding:18px">
    <div style="font-size:1.5rem;margin-bottom:6px">💻</div>
    <div style="font-size:.75rem;color:#6b7280;text-transform:uppercase;letter-spacing:.05em">终端活动</div>
    <div style="font-family:var(--font-mono);font-size:1.6rem;font-weight:700;color:#166534;margin:4px 0">{{CMD_COUNT}}</div>
    <div style="font-size:.8rem;color:#374151">条命令 · {{CMD_PROJECTS}} 个项目</div>
    <div style="font-size:.75rem;color:#6b7280;margin-top:8px">主要：{{CMD_TOP_CATEGORY}}</div>
  </div>

  <!-- AI Agent 卡片 -->
  <div class="ov-card" style="background:#fdf4ff;border:1.5px solid #d8b4fe;border-radius:12px;padding:18px">
    <div style="font-size:1.5rem;margin-bottom:6px">🤖</div>
    <div style="font-size:.75rem;color:#6b7280;text-transform:uppercase;letter-spacing:.05em">AI Agent</div>
    <div style="font-family:var(--font-mono);font-size:1.6rem;font-weight:700;color:#7c3aed;margin:4px 0">{{AGENT_SESSIONS}}</div>
    <div style="font-size:.8rem;color:#374151">次会话 · {{AGENT_TOOLS}}</div>
    <div style="font-size:.75rem;color:#6b7280;margin-top:8px">主任务：{{AGENT_MAIN_TASK}}</div>
  </div>

  <!-- 浏览器活动卡片 -->
  <div class="ov-card" style="background:#eff6ff;border:1.5px solid #93c5fd;border-radius:12px;padding:18px">
    <div style="font-size:1.5rem;margin-bottom:6px">🌐</div>
    <div style="font-size:.75rem;color:#6b7280;text-transform:uppercase;letter-spacing:.05em">浏览器</div>
    <div style="font-family:var(--font-mono);font-size:1.6rem;font-weight:700;color:#1d4ed8;margin:4px 0">{{BROWSER_VISITS}}</div>
    <div style="font-size:.8rem;color:#374151">次访问 · 技术 {{TECH_RATIO}}%</div>
    <div style="font-size:.75rem;color:#6b7280;margin-top:8px">娱乐：{{ENT_RATIO}}%</div>
  </div>

  <!-- 专注度卡片 -->
  <div class="ov-card" style="background:#fffbeb;border:1.5px solid #fcd34d;border-radius:12px;padding:18px">
    <div style="font-size:1.5rem;margin-bottom:6px">⚡</div>
    <div style="font-size:.75rem;color:#6b7280;text-transform:uppercase;letter-spacing:.05em">深度专注</div>
    <div style="font-family:var(--font-mono);font-size:1.6rem;font-weight:700;color:#d97706;margin:4px 0">{{FOCUS_BLOCKS}}</div>
    <div style="font-size:.8rem;color:#374151">个专注块 · 共 {{FOCUS_MINUTES}} 分钟</div>
    <div style="font-size:.75rem;color:#6b7280;margin-top:8px">高峰：{{PEAK_HOURS}}</div>
  </div>
</div>
```

### 区块2：时间分布 SVG 图表

```html
<div class="energy-wrap">
  <h3 style="font-size:.85rem;font-weight:700;margin-bottom:12px;color:var(--text-secondary)">TODAY'S ENERGY CURVE</h3>
  <svg class="energy-chart" viewBox="0 0 800 160" xmlns="http://www.w3.org/2000/svg">
    {{ENERGY_CURVE_SVG}}
  </svg>
  <!-- 图例 -->
  <div style="display:flex;gap:16px;margin-top:8px;font-size:.72rem;color:var(--text-secondary)">
    <span><span style="display:inline-block;width:10px;height:3px;background:#1d3557;border-radius:2px;vertical-align:middle;margin-right:4px"></span>终端</span>
    <span><span style="display:inline-block;width:10px;height:3px;background:#f59e0b;border-radius:2px;vertical-align:middle;margin-right:4px"></span>浏览器</span>
    <span><span style="display:inline-block;width:10px;height:3px;background:#7c3aed;border-radius:2px;vertical-align:middle;margin-right:4px"></span>Agent</span>
    <span><span style="display:inline-block;width:10px;height:3px;background:#d1d5db;border-radius:2px;vertical-align:middle;margin-right:4px"></span>空闲</span>
  </div>
</div>
```

### 区块3：AI 摘要卡片

```html
<div class="card">
  <h2>今日概览</h2>
  <p style="line-height:1.8;color:#374151">{{AI_NARRATIVE}}</p>
</div>
```

### 区块4：开发摘要卡片（可选，有开发数据时显示）

```html
<div class="card">
  <h2>开发 / 工作摘要</h2>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
    <div>
      <div style="font-size:.75rem;color:var(--text-secondary);margin-bottom:8px;text-transform:uppercase">涉及项目</div>
      {{PROJECT_TAGS_HTML}}
    </div>
    <div>
      <div style="font-size:.75rem;color:var(--text-secondary);margin-bottom:8px;text-transform:uppercase">命令分类</div>
      {{CMD_CATEGORY_BARS_HTML}}
    </div>
  </div>
</div>
```

---

## 洞察&技能页（#insights）完整结构规范

洞察&技能页（Tab 名称：🎯 洞察&技能）必须包含以下三个区块：

### 区块1：技能增强雷达

```html
<div class="skill-module">
  <h2 style="font-family:var(--font-serif);font-size:1.15rem;margin-bottom:16px">🎯 技能增强雷达</h2>
  <p style="font-size:.8rem;color:var(--text-secondary);margin-bottom:16px">基于今日操作日志自动识别的技能短板与提升机会</p>
  {{SKILL_ITEMS_HTML}}
  <!-- 无短板时 -->
  <!-- <div style="text-align:center;padding:24px;color:var(--text-secondary)">今日操作未发现明显短板 🎉</div> -->
</div>
```

### 区块2：命令统计表

```html
<div class="card">
  <h2>命令分类统计</h2>
  <table style="width:100%;border-collapse:collapse;font-size:.875rem">
    <thead>
      <tr style="background:#f9fafb">
        <th style="text-align:left;padding:10px 12px;border-bottom:2px solid var(--border)">类别</th>
        <th style="text-align:right;padding:10px 12px;border-bottom:2px solid var(--border)">数量</th>
        <th style="text-align:right;padding:10px 12px;border-bottom:2px solid var(--border)">占比</th>
        <th style="padding:10px 12px;border-bottom:2px solid var(--border)">分布</th>
      </tr>
    </thead>
    <tbody>
      {{CMD_STAT_ROWS_HTML}}
      <!-- 每行格式示例：
      <tr>
        <td style="padding:9px 12px;border-bottom:1px solid var(--border)">开发</td>
        <td style="text-align:right;padding:9px 12px;border-bottom:1px solid var(--border);font-family:var(--font-mono)">42</td>
        <td style="text-align:right;padding:9px 12px;border-bottom:1px solid var(--border);font-family:var(--font-mono)">58%</td>
        <td style="padding:9px 12px;border-bottom:1px solid var(--border)">
          <div style="height:6px;background:#1d3557;border-radius:3px;width:58%"></div>
        </td>
      </tr>
      -->
    </tbody>
  </table>
</div>
```

### 区块3：Obsidian 知识节点标签云

```html
<div class="card">
  <h2>🔮 Obsidian 知识节点</h2>
  <p style="font-size:.8rem;color:var(--text-secondary);margin-bottom:14px">可复制到 Obsidian 使用的双链标签</p>
  <!-- 话题标签 -->
  <div style="margin-bottom:12px">
    <div style="font-size:.72rem;color:var(--text-secondary);margin-bottom:8px;text-transform:uppercase;letter-spacing:.05em">今日标签</div>
    <div style="display:flex;flex-wrap:wrap;gap:8px">
      {{OBSIDIAN_HASHTAGS_HTML}}
      <!-- 每个标签：
      <span style="background:#e0f2fe;color:#0369a1;padding:4px 12px;border-radius:20px;
                   font-size:.8rem;font-family:var(--font-mono);cursor:pointer"
            onclick="navigator.clipboard.writeText(this.textContent)">#技能名</span>
      -->
    </div>
  </div>
  <!-- 双链节点 -->
  <div>
    <div style="font-size:.72rem;color:var(--text-secondary);margin-bottom:8px;text-transform:uppercase;letter-spacing:.05em">知识双链</div>
    <div style="display:flex;flex-wrap:wrap;gap:8px">
      {{OBSIDIAN_WIKILINKS_HTML}}
      <!-- 每个双链：
      <span style="background:#f0fdf4;color:#166534;padding:4px 12px;border-radius:20px;
                   font-size:.8rem;border:1px solid #86efac;cursor:pointer"
            onclick="navigator.clipboard.writeText(this.textContent)">[[概念名]]</span>
      -->
    </div>
  </div>
  <!-- 一键复制全部 -->
  <div style="margin-top:16px">
    <button onclick="copyObsidian()"
            style="background:var(--bg-header);color:#f7f4ef;border:none;padding:8px 16px;
                   border-radius:6px;cursor:pointer;font-size:.8rem;font-family:var(--font-sans)">
      📋 复制全部到 Obsidian
    </button>
  </div>
</div>

<script>
function copyObsidian() {
  const tags = [...document.querySelectorAll('#insights .card:last-child span')]
    .map(s => s.textContent).join(' ');
  navigator.clipboard.writeText(tags).then(() => {
    const btn = document.querySelector('#insights button');
    btn.textContent = '✅ 已复制'; setTimeout(() => btn.textContent = '📋 复制全部到 Obsidian', 2000);
  });
}
</script>
```

---

## Tab 导航按钮对应关系（必须严格匹配）

```html
<nav class="tabs">
  <button class="active" onclick="showTab('overview',this)">🏠 概览</button>
  <button onclick="showTab('timeline',this)">📋 时间线</button>
  <button onclick="showTab('insights',this)">🎯 洞察&技能</button>
  <button onclick="showTab('growth',this)">📈 成长轨迹</button>
  <button onclick="showTab('experts',this)">🧠 专家委员会</button>
  <button onclick="showTab('tomorrow',this)">🚀 明日行动</button>
</nav>
```

对应 section id：`overview` / `timeline` / `insights` / `growth` / `experts` / `tomorrow`

> 注意：原模板 Tab 顺序已更新，将"洞察&技能"移至时间线后、成长轨迹前，与 lifelog-daily 对齐。
