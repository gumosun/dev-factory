#!/usr/bin/env python3
"""token-lens Ledger — 解析 Claude Code transcripts,產出 token 用量與成本帳本。
只讀 usage 統計與 model/agentType 欄位,不讀對話內容。
"""
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude" / "projects"
OUT_DIR = Path(__file__).parent / "out"

# API 等值定價 (USD per token)。cache write: 5m=1.25x input, 1h=2x input; cache read=0.1x input
PRICING = {
    # model prefix -> (input, output) per MTok
    "claude-fable-5": (10.0, 50.0),
    "claude-mythos": (10.0, 50.0),
    "claude-opus": (5.0, 25.0),
    "claude-sonnet": (3.0, 15.0),
    "claude-haiku": (1.0, 5.0),
}

def price_for(model: str):
    for prefix, p in PRICING.items():
        if model.startswith(prefix):
            return p
    return None

def parse_file(path: Path, project: str, source: str, agent_type: str, rows: dict):
    """rows: message_id -> row dict (dedup across streaming duplicates)"""
    try:
        fh = open(path, "r", errors="replace")
    except OSError:
        return
    with fh:
        for line in fh:
            if '"assistant"' not in line or '"usage"' not in line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("type") != "assistant":
                continue
            m = d.get("message") or {}
            u = m.get("usage") or {}
            mid = m.get("id")
            if not mid:
                continue
            cc = u.get("cache_creation") or {}
            row = {
                "project": project,
                "source": source,
                "agent_type": agent_type,
                "model": m.get("model", "unknown"),
                "ts": (d.get("timestamp") or "")[:10],
                "input": u.get("input_tokens", 0) or 0,
                "output": u.get("output_tokens", 0) or 0,
                "cache_read": u.get("cache_read_input_tokens", 0) or 0,
                "cache_w_5m": cc.get("ephemeral_5m_input_tokens"),
                "cache_w_1h": cc.get("ephemeral_1h_input_tokens"),
                "cache_w_total": u.get("cache_creation_input_tokens", 0) or 0,
            }
            # 同一 message id 出現多次(streaming 快照)→ 保留 output 最大的那筆
            prev = rows.get(mid)
            if prev is None or row["output"] >= prev["output"]:
                rows[mid] = row

def cost_of(row):
    p = price_for(row["model"])
    if not p:
        return 0.0
    in_p, out_p = p[0] / 1e6, p[1] / 1e6
    w5 = row["cache_w_5m"]
    w1 = row["cache_w_1h"]
    if w5 is None and w1 is None:
        # 舊格式沒有 TTL 細分,保守用 1.25x
        cache_write_cost = row["cache_w_total"] * in_p * 1.25
    else:
        cache_write_cost = (w5 or 0) * in_p * 1.25 + (w1 or 0) * in_p * 2.0
    return (
        row["input"] * in_p
        + row["output"] * out_p
        + row["cache_read"] * in_p * 0.1
        + cache_write_cost
    )

def main():
    # --project auto|<name>: 只計算單一專案(auto=從 cwd 推導),供 retro 在專案內零 token 呼叫
    only = None
    if "--project" in sys.argv:
        val = sys.argv[sys.argv.index("--project") + 1]
        only = str(Path.cwd()).replace("/", "-") if val == "auto" else val
    rows = {}
    n_files = 0
    for proj_dir in sorted(PROJECTS_DIR.iterdir()):
        if not proj_dir.is_dir():
            continue
        if only and proj_dir.name != only:
            continue
        project = proj_dir.name.replace("-Users-haosun-", "").replace("Desktop-", "") or "home"
        # 主 session transcripts
        for f in proj_dir.glob("*.jsonl"):
            parse_file(f, project, "main", "main", rows)
            n_files += 1
        # subagent transcripts (session 子目錄底下)
        for agent_file in proj_dir.glob("*/subagents/agent-*.jsonl"):
            meta_path = agent_file.with_suffix("").with_suffix("")  # strip .jsonl
            meta_file = agent_file.parent / (agent_file.stem + ".meta.json")
            agent_type = "subagent"
            if meta_file.exists():
                try:
                    agent_type = json.load(open(meta_file)).get("agentType") or "subagent"
                except Exception:
                    pass
            parse_file(agent_file, project, "subagent", agent_type, rows)
            n_files += 1

    # ---- 聚合 ----
    def agg(key_fn):
        acc = defaultdict(lambda: {"msgs": 0, "input": 0, "output": 0, "cache_read": 0, "cache_write": 0, "cost": 0.0})
        for r in rows.values():
            k = key_fn(r)
            a = acc[k]
            a["msgs"] += 1
            a["input"] += r["input"]
            a["output"] += r["output"]
            a["cache_read"] += r["cache_read"]
            a["cache_write"] += r["cache_w_total"]
            a["cost"] += cost_of(r)
        return dict(acc)

    by_project = agg(lambda r: r["project"])
    by_model = agg(lambda r: r["model"])
    by_role = agg(lambda r: (r["project"], r["agent_type"]))
    by_month = agg(lambda r: r["ts"][:7] if r["ts"] else "unknown")

    total = {"msgs": len(rows)}
    for k in ("input", "output", "cache_read", "cache_write"):
        total[k] = sum(r[k] if k != "cache_write" else r["cache_w_total"] for r in rows.values())
    total["cost"] = sum(cost_of(r) for r in rows.values())

    OUT_DIR.mkdir(exist_ok=True)
    with open(OUT_DIR / "ledger.json", "w") as f:
        json.dump({
            "total": total,
            "by_project": by_project,
            "by_model": by_model,
            "by_role": {f"{p}::{a}": v for (p, a), v in by_role.items()},
            "by_month": by_month,
            "files_scanned": n_files,
        }, f, ensure_ascii=False, indent=1)

    # ---- 報表 ----
    def fmt(n):
        if n >= 1e9: return f"{n/1e9:.2f}B"
        if n >= 1e6: return f"{n/1e6:.1f}M"
        if n >= 1e3: return f"{n/1e3:.0f}K"
        return str(n)

    print(f"檔案 {n_files} 個 | 去重後 assistant 訊息 {len(rows):,} 筆")
    print(f"\n== 總計 ==")
    print(f"output: {fmt(total['output'])} | fresh input: {fmt(total['input'])} | cache read: {fmt(total['cache_read'])} | cache write: {fmt(total['cache_write'])}")
    print(f"API 等值成本: ${total['cost']:,.2f}")
    denom = total['input'] + total['cache_read'] + total['cache_write']
    if denom:
        print(f"cache 命中率(read/(read+fresh+write)): {total['cache_read']/denom*100:.1f}%")

    print(f"\n== 按專案 (成本前 12) ==")
    for k, v in sorted(by_project.items(), key=lambda x: -x[1]["cost"])[:12]:
        print(f"  {k:42s} ${v['cost']:9,.2f} | out {fmt(v['output']):>7} | read {fmt(v['cache_read']):>7} | msgs {v['msgs']}")

    print(f"\n== 按模型 ==")
    for k, v in sorted(by_model.items(), key=lambda x: -x[1]["cost"]):
        print(f"  {k:32s} ${v['cost']:9,.2f} | out {fmt(v['output']):>7} | msgs {v['msgs']}")

    print(f"\n== 按月份 ==")
    for k, v in sorted(by_month.items()):
        print(f"  {k}  ${v['cost']:9,.2f} | out {fmt(v['output']):>7}")

    print(f"\n== dev-factory / discovery 角色歸戶 (成本前 15) ==")
    role_rows = [(f"{p} :: {a}", v) for (p, a), v in by_role.items() if a not in ("main",)]
    for k, v in sorted(role_rows, key=lambda x: -x[1]["cost"])[:15]:
        print(f"  {k:52s} ${v['cost']:8,.2f} | out {fmt(v['output']):>7} | msgs {v['msgs']}")

if __name__ == "__main__":
    main()
