#!/usr/bin/env python3
"""
LifeLog Pro · 跨平台自动数据采集脚本
支持：Windows / macOS / Linux
输出：/tmp/lifelog-collect/collected_data.json
"""

import os
import sys
import json
import glob
import shutil
import platform
import subprocess
import datetime
from pathlib import Path

OUTPUT_DIR = Path("/tmp/lifelog-collect")
OUTPUT_FILE = OUTPUT_DIR / "collected_data.json"
TODAY = datetime.date.today().isoformat()
OS = platform.system()  # 'Darwin', 'Linux', 'Windows'

collected = {
    "date": TODAY,
    "os": OS,
    "sources": {},
    "errors": {}
}

def log_ok(source, data):
    collected["sources"][source] = data
    print(f"  ✅ {source}: 采集成功")

def log_fail(source, reason):
    collected["errors"][source] = str(reason)
    print(f"  ⚠️  {source}: 跳过 ({reason})")

# ─────────────────────────────────────────────
# 1. Shell History
# ─────────────────────────────────────────────
def collect_shell_history():
    history_lines = []

    # macOS / Linux
    candidates = [
        Path.home() / ".zsh_history",
        Path.home() / ".bash_history",
        Path.home() / ".local/share/fish/fish_history",
        Path.home() / ".history",
    ]

    # Windows PowerShell
    if OS == "Windows":
        ps_history = Path.home() / "AppData/Roaming/Microsoft/Windows/PowerShell/PSReadLine/ConsoleHost_history.txt"
        candidates.append(ps_history)

    found = False
    for path in candidates:
        if path.exists():
            try:
                content = path.read_text(errors="replace")
                lines = [l.strip() for l in content.splitlines() if l.strip()]
                # Fish history format conversion
                if "fish" in str(path):
                    lines = [l.replace("- cmd: ", "") for l in lines if l.startswith("- cmd:")]
                history_lines.extend(lines[-2000:])  # last 2000 lines
                found = True
            except Exception as e:
                pass

    if found:
        log_ok("shell_history", {"lines": history_lines, "count": len(history_lines)})
    else:
        log_fail("shell_history", "未找到历史文件")

# ─────────────────────────────────────────────
# 2. AI Agent 对话记录
# ─────────────────────────────────────────────
def collect_agent_logs():
    agents = {}

    # Claude Code: ~/.claude/
    claude_dir = Path.home() / ".claude"
    if claude_dir.exists():
        logs = list(claude_dir.glob("**/*.json"))[:50]
        if logs:
            entries = []
            for lf in logs:
                try:
                    stat = lf.stat()
                    mtime = datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
                    if TODAY in mtime:
                        data = json.loads(lf.read_text(errors="replace"))
                        entries.append({"file": str(lf.name), "modified": mtime, "preview": str(data)[:300]})
                except:
                    pass
            if entries:
                agents["claude_code"] = entries

    # Cursor: ~/.cursor/logs/
    cursor_dir = Path.home() / ".cursor" / "logs"
    if cursor_dir.exists():
        logs = sorted(cursor_dir.glob("*.log"), key=os.path.getmtime, reverse=True)[:5]
        entries = []
        for lf in logs:
            try:
                stat = lf.stat()
                mtime = datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
                if TODAY in mtime:
                    entries.append({"file": lf.name, "modified": mtime, "size": stat.st_size})
            except:
                pass
        if entries:
            agents["cursor"] = entries

    # Codex / OpenAI CLI: ~/.openai/
    openai_dir = Path.home() / ".openai"
    if openai_dir.exists():
        logs = list(openai_dir.glob("**/*.json"))[:20]
        if logs:
            agents["codex"] = [{"file": str(f.name)} for f in logs]

    # Hermes / local LLM logs
    for hermes_path in [Path.home() / ".hermes", Path("/tmp/hermes"), Path("./hermes_logs")]:
        if hermes_path.exists():
            agents["hermes"] = {"path": str(hermes_path), "found": True}
            break

    if agents:
        log_ok("agent_logs", agents)
    else:
        log_fail("agent_logs", "未找到 agent 对话记录")

# ─────────────────────────────────────────────
# 3. 浏览器历史
# ─────────────────────────────────────────────
def collect_browser_history():
    import sqlite3, tempfile

    browser_paths = {}

    if OS == "Darwin":
        browser_paths = {
            "chrome": Path.home() / "Library/Application Support/Google/Chrome/Default/History",
            "firefox": next(iter(Path.home().glob("Library/Application Support/Firefox/Profiles/*.default*/places.sqlite")), None),
            "edge": Path.home() / "Library/Application Support/Microsoft Edge/Default/History",
            "safari": Path.home() / "Library/Safari/History.db",
        }
    elif OS == "Linux":
        browser_paths = {
            "chrome": Path.home() / ".config/google-chrome/Default/History",
            "chromium": Path.home() / ".config/chromium/Default/History",
            "firefox": next(iter(Path.home().glob(".mozilla/firefox/*.default*/places.sqlite")), None),
            "edge": Path.home() / ".config/microsoft-edge/Default/History",
        }
    elif OS == "Windows":
        appdata = Path(os.environ.get("LOCALAPPDATA", ""))
        browser_paths = {
            "chrome": appdata / "Google/Chrome/User Data/Default/History",
            "edge": appdata / "Microsoft/Edge/User Data/Default/History",
            "firefox": next(iter(Path.home().glob("AppData/Roaming/Mozilla/Firefox/Profiles/*.default*/places.sqlite")), None),
        }

    results = {}
    today_start = int(datetime.datetime.combine(datetime.date.today(), datetime.time.min).timestamp())

    for browser, db_path in browser_paths.items():
        if not db_path or not Path(db_path).exists():
            continue
        try:
            # Copy DB to avoid lock issues
            with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
                tmp_path = tmp.name
            shutil.copy2(db_path, tmp_path)

            conn = sqlite3.connect(tmp_path)
            cur = conn.cursor()

            if browser in ("chrome", "chromium", "edge"):
                # Chrome epoch: microseconds since 1601-01-01
                chrome_epoch_offset = 11644473600
                today_chrome = (today_start + chrome_epoch_offset) * 1000000
                cur.execute("""
                    SELECT datetime((last_visit_time/1000000)-11644473600, 'unixepoch'),
                           url, title
                    FROM urls
                    WHERE last_visit_time > ?
                    ORDER BY last_visit_time DESC LIMIT 500
                """, (today_chrome,))
            elif browser == "firefox":
                cur.execute("""
                    SELECT datetime(last_visit_date/1000000, 'unixepoch'),
                           url, title
                    FROM moz_places
                    WHERE last_visit_date > ?
                    ORDER BY last_visit_date DESC LIMIT 500
                """, (today_start * 1000000,))
            elif browser == "safari":
                cur.execute("""
                    SELECT datetime(v.visit_time + 978307200, 'unixepoch'),
                           i.url, v.title
                    FROM history_visits v
                    JOIN history_items i ON v.history_item = i.id
                    WHERE v.visit_time > ?
                    ORDER BY v.visit_time DESC LIMIT 500
                """, (today_start - 978307200,))
            else:
                conn.close()
                os.unlink(tmp_path)
                continue

            rows = cur.fetchall()
            conn.close()
            os.unlink(tmp_path)

            # Filter sensitive URLs
            sensitive_keywords = ["login", "account", "pay", "bank", "password", "auth", "token"]
            safe_rows = []
            for time_str, url, title in rows:
                if any(kw in url.lower() for kw in sensitive_keywords):
                    safe_rows.append({"time": time_str, "url": "[已隐去敏感URL]", "title": title or ""})
                else:
                    safe_rows.append({"time": time_str, "url": url, "title": title or ""})

            results[browser] = safe_rows
        except Exception as e:
            collected["errors"][f"browser_{browser}"] = str(e)

    if results:
        log_ok("browser_history", results)
    else:
        log_fail("browser_history", "无法读取浏览器历史（可能需要关闭浏览器后重试）")

# ─────────────────────────────────────────────
# 4. 软件/窗口使用记录
# ─────────────────────────────────────────────
def collect_app_usage():
    apps = {}

    if OS == "Darwin":
        # macOS: 使用 lsappinfo / ps
        try:
            result = subprocess.run(
                ["ps", "-eo", "comm,%cpu,%mem", "--sort=-%cpu"],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().splitlines()[1:30]  # top 30 apps
            apps["process_snapshot"] = [l.strip() for l in lines if l.strip()]
            log_ok("app_usage", apps)
        except Exception as e:
            log_fail("app_usage", e)

    elif OS == "Linux":
        try:
            result = subprocess.run(
                ["ps", "-eo", "comm,%cpu,%mem", "--sort=-%cpu"],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().splitlines()[1:30]
            apps["process_snapshot"] = [l.strip() for l in lines if l.strip()]

            # Try wmctrl for window titles
            if shutil.which("wmctrl"):
                r2 = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True, timeout=3)
                apps["window_list"] = r2.stdout.strip().splitlines()

            log_ok("app_usage", apps)
        except Exception as e:
            log_fail("app_usage", e)

    elif OS == "Windows":
        try:
            ps_cmd = "Get-Process | Sort-Object CPU -Descending | Select-Object -First 30 Name,CPU,WorkingSet | ConvertTo-Json"
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True, text=True, timeout=10
            )
            apps["process_snapshot"] = json.loads(result.stdout) if result.stdout.strip() else []
            log_ok("app_usage", apps)
        except Exception as e:
            log_fail("app_usage", e)

# ─────────────────────────────────────────────
# 5. 最近编辑文件
# ─────────────────────────────────────────────
def collect_recent_files():
    recent = []

    if OS == "Darwin":
        try:
            result = subprocess.run(
                ["mdfind", f"kMDItemContentModificationDate >= '{TODAY}T00:00:00'",
                 "-onlyin", str(Path.home()), "-name", "*.py", "-name", "*.js",
                 "-name", "*.ts", "-name", "*.md", "-name", "*.go", "-name", "*.rs"],
                capture_output=True, text=True, timeout=10
            )
            files = [f for f in result.stdout.strip().splitlines() if f]
            recent = files[:50]
        except Exception as e:
            log_fail("recent_files", e)
            return

    elif OS == "Linux":
        try:
            result = subprocess.run(
                ["find", str(Path.home()), "-newer",
                 f"/tmp/.lifelog_marker_{TODAY}", "-type", "f",
                 "-name", "*.py", "-o", "-name", "*.js", "-o",
                 "-name", "*.ts", "-o", "-name", "*.md",
                 "-o", "-name", "*.go", "-o", "-name", "*.rs"],
                capture_output=True, text=True, timeout=10
            )
            recent = result.stdout.strip().splitlines()[:50]
        except Exception as e:
            log_fail("recent_files", e)
            return

    elif OS == "Windows":
        try:
            ps_cmd = f"""
            Get-ChildItem -Path $HOME -Recurse -Include *.py,*.js,*.ts,*.md,*.go,*.rs `
              -ErrorAction SilentlyContinue |
              Where-Object {{ $_.LastWriteTime -gt (Get-Date).Date }} |
              Select-Object -First 50 FullName |
              ConvertTo-Json
            """
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout) if result.stdout.strip() else []
            recent = [d["FullName"] for d in (data if isinstance(data, list) else [data])]
        except Exception as e:
            log_fail("recent_files", e)
            return

    if recent:
        log_ok("recent_files", {"files": recent, "count": len(recent)})
    else:
        log_fail("recent_files", "未找到今日编辑文件")

# ─────────────────────────────────────────────
# 6. 历史日志扫描
# ─────────────────────────────────────────────
def collect_past_logs():
    scan_paths = [
        "/mnt/user-data/outputs/daily_*.md",
        str(Path.home() / "lifelog/daily_*.md"),
        str(Path.home() / "Documents/lifelog/daily_*.md"),
        str(Path.home() / "Desktop/lifelog/daily_*.md"),
        "./daily_*.md",
    ]

    found_logs = []
    cutoff = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()

    for pattern in scan_paths:
        for fpath in glob.glob(pattern):
            fname = Path(fpath).name
            # Extract date from filename: daily_YYYY-MM-DD.md
            try:
                date_str = fname.replace("daily_", "").replace(".md", "")
                if date_str >= cutoff:
                    content = Path(fpath).read_text(errors="replace")
                    found_logs.append({
                        "date": date_str,
                        "path": fpath,
                        "content_preview": content[:3000],
                        "full_length": len(content)
                    })
            except:
                pass

    found_logs.sort(key=lambda x: x["date"], reverse=True)

    if found_logs:
        log_ok("past_logs", {"count": len(found_logs), "logs": found_logs[:30]})
    else:
        log_fail("past_logs", "未找到过去30天的历史日志（首次生成属正常）")

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n🚀 LifeLog Pro v2 · 自动采集 [{OS}] · {TODAY}\n")
    print("─" * 50)

    collect_shell_history()
    collect_agent_logs()
    collect_browser_history()
    collect_app_usage()
    collect_recent_files()
    collect_past_logs()
    analyze_second_order_signals()

    print("─" * 50)
    success = len(collected["sources"])
    fail = len(collected["errors"])
    print(f"\n✨ 完成！成功 {success} 个数据源，跳过 {fail} 个。")
    print(f"📦 输出：{OUTPUT_FILE}\n")

    OUTPUT_FILE.write_text(json.dumps(collected, ensure_ascii=False, indent=2))
    return str(OUTPUT_FILE)

if __name__ == "__main__":
    main()

# ─────────────────────────────────────────────
# 7. 二阶信号：命令时间间隔 → 能量曲线 + 专注块
# ─────────────────────────────────────────────
def analyze_second_order_signals():
    """
    从带时间戳的 shell history 计算：
    - 每小时命令密度（能量曲线数据点）
    - 专注块（连续工作段，间隔<5min）
    - 分心指数（工具切换频率估算）
    """
    shell_data = collected["sources"].get("shell_history", {})
    lines = shell_data.get("lines", [])

    timestamps = []
    for line in lines:
        # 尝试解析多种时间戳格式
        import re
        patterns = [
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',  # 2025-05-13 09:32:15
            r'(\d{2}:\d{2}:\d{2})',                      # 09:32:15
        ]
        for pat in patterns:
            m = re.search(pat, line)
            if m:
                try:
                    ts_str = m.group(1)
                    if len(ts_str) == 8:  # HH:MM:SS only
                        ts_str = f"{TODAY} {ts_str}"
                    ts = datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                    timestamps.append(ts)
                    break
                except:
                    pass

    if len(timestamps) < 2:
        log_fail("second_order", "history 无时间戳，跳过二阶信号分析")
        return

    timestamps.sort()
    today_ts = [t for t in timestamps if t.date().isoformat() == TODAY]

    if not today_ts:
        log_fail("second_order", "今日无带时间戳的命令")
        return

    # 每小时密度
    hourly = [0] * 24
    for t in today_ts:
        hourly[t.hour] += 1
    max_density = max(hourly) or 1
    energy_curve = [{"hour": h, "density": round(c / max_density, 2)} for h, c in enumerate(hourly)]

    # 专注块：间隔 > 5min 视为中断
    focus_blocks = []
    block_start = today_ts[0]
    prev = today_ts[0]
    for t in today_ts[1:]:
        gap = (t - prev).total_seconds() / 60
        if gap > 5:
            duration = (prev - block_start).total_seconds() / 60
            if duration >= 15:  # 至少15分钟才算专注块
                focus_blocks.append({
                    "start": block_start.strftime("%H:%M"),
                    "end": prev.strftime("%H:%M"),
                    "duration_min": round(duration)
                })
            block_start = t
        prev = t
    # 最后一个块
    duration = (prev - block_start).total_seconds() / 60
    if duration >= 15:
        focus_blocks.append({
            "start": block_start.strftime("%H:%M"),
            "end": prev.strftime("%H:%M"),
            "duration_min": round(duration)
        })

    total_focus_min = sum(b["duration_min"] for b in focus_blocks)

    result = {
        "energy_curve": energy_curve,
        "focus_blocks": focus_blocks,
        "focus_block_count": len(focus_blocks),
        "total_focus_minutes": total_focus_min,
        "peak_hour": max(range(24), key=lambda h: hourly[h]),
        "low_hour": min(range(8, 23), key=lambda h: hourly[h]),  # 工作时段内最低
    }

    log_ok("second_order", result)

