# LifeLog Pro · 周报聚合算法

## 触发条件

用户说以下任意词时进入周报模式：
"周报"、"本周"、"weekly"、"this week"、"本周总结"、"一周回顾"

## 数据加载

```python
# 扫描过去7天的日报文件
from datetime import date, timedelta
import glob, json

today = date.today()
week_logs = []
for i in range(1, 8):  # 过去7天（不含今天，今天用日报）
    d = (today - timedelta(days=i)).isoformat()
    for pattern in [
        f"/mnt/user-data/outputs/daily_{d}.md",
        f"~/lifelog/daily_{d}.md",
        f"./daily_{d}.md",
    ]:
        matches = glob.glob(pattern)
        if matches:
            week_logs.append({"date": d, "path": matches[0]})
            break

# 也包含今天（如果今天日报已生成）
today_log_pattern = f"/mnt/user-data/outputs/daily_{today.isoformat()}.md"
```

## 聚合维度

### 1. 能量曲线周对比

从每份日报提取能量曲线数据点（或命令密度数组），叠加到一张 SVG 图上：
- x轴：0-24小时
- y轴：归一化密度
- 每天一条颜色不同的折线
- 标注最高效的一天（折线面积最大）

若日报中无结构化能量数据，从命令时间戳估算。

### 2. 项目时间矩阵

```
项目名      | 周一 | 周二 | 周三 | 周四 | 周五 | 周六 | 周日 | 总计
project-x   |  2h  |  0   |  3h  |  1h  |  0   |  2h  |  0   |  8h
project-y   |  0   |  4h  |  0   |  2h  |  1h  |  0   |  0   |  7h
```

### 3. 技能短板追踪矩阵

```python
# 从每份日报的"技能增强雷达"章节提取短板
weekly_weaknesses = {}
for log in week_logs:
    for weakness in log["skill_items"]:
        name = weakness["name"]
        if name not in weekly_weaknesses:
            weekly_weaknesses[name] = {"count": 0, "days": [], "level": weakness["level"]}
        weekly_weaknesses[name]["count"] += 1
        weekly_weaknesses[name]["days"].append(log["date"])

# 分类
persistent = [w for w in weekly_weaknesses.values() if w["count"] >= 3]  # 本周3天以上出现
occasional = [w for w in weekly_weaknesses.values() if w["count"] < 3]
```

### 4. 行为模式周统计

```python
weekly_stats = {
    "total_commands": sum(log["cmd_count"] for log in week_logs),
    "total_focus_minutes": sum(log["focus_minutes"] for log in week_logs),
    "avg_daily_work_hours": mean(log["work_hours"] for log in week_logs),
    "entertainment_ratio": mean(log["entertainment_ratio"] for log in week_logs),
    "best_day": max(week_logs, key=lambda x: x["focus_minutes"]),
    "worst_day": min(week_logs, key=lambda x: x["focus_minutes"]),
    "total_agent_sessions": sum(log["agent_sessions"] for log in week_logs),
}
```

### 5. 拐点识别（周维度）

在7天数据上运行拐点算法：
```python
# 专注度序列
focus_sequence = [log["focus_minutes"] for log in sorted(week_logs, key=lambda x: x["date"])]

# 找最大跌幅
max_drop = 0
drop_day = None
for i in range(1, len(focus_sequence)):
    drop = focus_sequence[i-1] - focus_sequence[i]
    if drop > max_drop:
        max_drop = drop
        drop_day = week_logs[i]["date"]

if max_drop > 30:  # 超过30分钟的跌幅视为显著拐点
    # 输出："你的专注度在{drop_day}出现明显下滑（-{max_drop}分钟），
    #        那天你主要在做：{week_logs[i]['top_activity']}"
```

## 周报输出文件

文件名：
- `weekly_YYYY-WNN.md` （WNN = ISO周数，如 W22）
- `weekly_YYYY-WNN.html`

HTML 结构（五 Tab）：
```
概览 / 能量对比 / 项目矩阵 / 技能追踪 / 专家委员会·周度版
```

## 周报专家委员会

与日报相同的五位专家，但信息来源扩展：
- 用户数据 = 7天聚合数据
- 新闻 = 本周重要新闻（搜索 "this week AI tech news" 等）
- 综合专家的"明日行动"升级为"下周最重要的一件事"

## 数据不足降级

| 可用日报数 | 处理方式 |
|-----------|---------|
| 7天完整 | 正常生成 |
| 3-6天 | 生成，标注缺失天 |
| 1-2天 | 生成，标注"数据不足，仅供参考" |
| 0天 | 提示用户先生成日报 |
