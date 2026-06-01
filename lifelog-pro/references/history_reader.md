# LifeLog Pro · 历史日记读取与拐点分析

## 扫描路径（优先级）

```
1. /mnt/user-data/outputs/daily_*.md
2. ~/lifelog/daily_*.md
3. ~/Documents/lifelog/daily_*.md
4. ~/Desktop/lifelog/daily_*.md
5. ./daily_*.md
```

文件名格式必须为 `daily_YYYY-MM-DD.md`，否则跳过。
时间范围：过去 30 天。

## 提取字段

从每份历史日志中提取：

| 字段 | 来源 |
|------|------|
| date | 文件名 or YAML frontmatter |
| projects | `## 开发/工作记录` → 项目列表 |
| cmd_count | `命令分类统计` 表格合计 |
| skill_items | `## 技能增强雷达` 各条目 |
| achievements | `## 今日成就` |
| pending | `## 待续` |
| focus_minutes | `专注块` 相关数字（如有） |
| work_hours | 工作时长估算 |
| energy_curve | 能量曲线数据点（如有） |
| psych_signal | `## 三维分析 → 心理` 章节 |

## 拐点识别算法

### 专注度拐点

```python
# 提取过去N天的专注度序列
focus_seq = sorted([(log.date, log.focus_minutes) for log in history_logs])

# 计算3日均值
rolling_avg = []
for i in range(2, len(focus_seq)):
    avg = mean([focus_seq[j][1] for j in range(i-2, i+1)])
    rolling_avg.append((focus_seq[i][0], avg))

# 今日 vs 前3日均值
today_focus = today_data.focus_minutes
recent_avg = mean([focus_seq[-1][1], focus_seq[-2][1], focus_seq[-3][1]])

if today_focus < recent_avg * 0.7:
    # 下滑超30%，识别为拐点
    output: f"你的专注度今天比过去3天均值低{pct}%，
             过去3天最高产的一天是{best_day}（{best_minutes}分钟深度工作）。
             是什么让今天的状态发生了变化？"

elif today_focus > recent_avg * 1.3:
    # 上升超30%
    output: f"今天是你近期最高产的一天（超过过去3日均值{pct}%），
             高峰时段在{peak_hour}，主要在做{peak_activity}。"
```

### 项目停滞拐点

```python
for project in all_projects_ever_seen:
    last_seen = max(log.date for log in history_logs if project in log.projects)
    days_gap = (today - last_seen).days
    
    if days_gap > 14:
        level = "🔴 严重搁置"
    elif days_gap > 7:
        level = "🟡 停滞警告"
    else:
        continue
    
    output: f"{level}：{project} 已 {days_gap} 天未出现在日志中（上次：{last_seen}）"
```

### 技能短板复现追踪

```python
weakness_history = {}
for log in history_logs:
    for skill in log.skill_items:
        name = skill.name
        weakness_history.setdefault(name, []).append(log.date)

for name, dates in weakness_history.items():
    count = len(dates)
    if count >= 3:
        label = f"🔴 持续短板（已出现{count}次：{', '.join(dates[-3:])}）"
    elif name in today_skills:
        label = f"🟡 再次出现（上次：{dates[-1]}）"
    # 输出到成长轨迹章节
```

## 无历史日志（首次运行）

输出固定文本：
```markdown
## 📈 成长轨迹

> 这是你的第一份 LifeLog Pro 日志。
> 从明天起，这里将显示你的连续工作轨迹、拐点分析和技能成长曲线。
> 数据越积累，分析越精准。
```

## 隐私说明

历史日志仅本地读取，不上传，不发送外部。
用户可在触发时说"不要读取历史"，跳过此阶段。
