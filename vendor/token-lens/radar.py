#!/usr/bin/env python3
"""token-lens Radar v0 — 模型情報雷達。
定期抓取 Anthropic 官方模型/定價文件,與本地 catalog 比對,有變動即產出報告並標記受影響的路由政策。
Pattern 移植自 P2 文獻雷達(fetch → diff → analyze → report)。
用法: python3 radar.py        # 抓取+比對+報告
     每週跑一次(cron/launchd 或 Claude Code /schedule)
"""
import hashlib
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

BASE = Path(__file__).parent
CATALOG = BASE / "catalog.json"
REPORT = BASE / "out" / "radar-report.md"

SOURCES = {
    "models": "https://platform.claude.com/docs/en/about-claude/models/overview.md",
    "pricing": "https://platform.claude.com/docs/en/pricing.md",
}

MODEL_ID_RE = re.compile(r"claude-[a-z0-9][a-z0-9.-]+")
# 合法 model id 形狀: family-major(-minor)?(-YYYYMMDD)?(-vN)? — 過濾 markdown 錨點碎片
VALID_ID_RE = re.compile(
    r"^claude-(?:(?:fable|mythos|sonnet)-\d|mythos-preview|(?:opus|sonnet|haiku)-\d-\d)"
    r"(?:-\d{8})?(?:-v\d)?$"
)
PRICE_RE = re.compile(r"\$(\d+(?:\.\d+)?)\s*(?:/|per)?\s*(?:1M|million|MTok)", re.I)

def fetch(url: str) -> str:
    r = subprocess.run(["curl", "-sL", "--max-time", "30", url], capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError(f"fetch failed: {url}")
    return r.stdout

def snapshot():
    snap = {"date": str(date.today()), "sources": {}}
    for name, url in SOURCES.items():
        text = fetch(url)
        model_ids = sorted({m for m in MODEL_ID_RE.findall(text) if VALID_ID_RE.match(m)})
        prices = PRICE_RE.findall(text)
        snap["sources"][name] = {
            "hash": hashlib.sha256(text.encode()).hexdigest()[:16],
            "model_ids": model_ids,
            "price_points": sorted(set(prices), key=float),
        }
    return snap

def diff(old, new):
    changes = []
    for name in SOURCES:
        o = (old or {}).get("sources", {}).get(name, {})
        n = new["sources"][name]
        if not o:
            changes.append(f"- `{name}`: 首次建立基準(hash {n['hash']})")
            continue
        if o.get("hash") == n["hash"]:
            continue
        added = set(n["model_ids"]) - set(o.get("model_ids", []))
        removed = set(o.get("model_ids", [])) - set(n["model_ids"])
        p_added = set(n["price_points"]) - set(o.get("price_points", []))
        p_removed = set(o.get("price_points", [])) - set(n["price_points"])
        if added:
            changes.append(f"- `{name}` 🆕 新模型 id: {', '.join(sorted(added))}")
        if removed:
            changes.append(f"- `{name}` ⚠️ 消失的模型 id(可能退役): {', '.join(sorted(removed))}")
        if p_added or p_removed:
            changes.append(f"- `{name}` 💰 價格點變動: +{sorted(p_added)} / -{sorted(p_removed)}")
        if not (added or removed or p_added or p_removed):
            changes.append(f"- `{name}` 內容更新(hash 變動,無模型/價格結構變化)——可能是文件改版,值得掃一眼")
    return changes

def main():
    old = json.loads(CATALOG.read_text()) if CATALOG.exists() else None
    try:
        new = snapshot()
    except RuntimeError as e:
        print(f"[radar] {e}", file=sys.stderr)
        sys.exit(1)
    changes = diff(old, new)
    CATALOG.write_text(json.dumps(new, indent=1))
    REPORT.parent.mkdir(exist_ok=True)
    lines = [f"# Radar 報告 — {new['date']}", ""]
    if changes:
        lines += ["## 變動"] + changes + ["", "## 對路由政策的影響",
                  "有模型/價格變動時:重跑 `ledger.py` 用新價格計算成本、檢查 `router-policy.yaml` 的層級指派是否仍是成本最優、若有新模型先跑小樣本 gate 實驗再納入政策。"]
    else:
        lines += ["無變動。政策維持現狀。"]
    lines += ["", f"監測來源: {', '.join(SOURCES.values())}",
              "已知模型: " + ", ".join(new["sources"]["models"]["model_ids"][:20])]
    REPORT.write_text("\n".join(lines))
    print("\n".join(lines))

if __name__ == "__main__":
    main()
