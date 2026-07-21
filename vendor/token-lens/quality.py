#!/usr/bin/env python3
"""token-lens Quality — 角色×模型的工作組成 + 品質摩擦訊號(工具錯誤率)。
錯誤歸戶方式:tool_result 的 is_error 掛在 user entry,取同檔案內最近一筆 assistant 的 model。
"""
import json
from collections import defaultdict
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude" / "projects"

def scan_file(path: Path, project: str, agent_type: str, acc, seen_msgs):
    cur_model = None
    try:
        fh = open(path, "r", errors="replace")
    except OSError:
        return
    with fh:
        for line in fh:
            has_asst = '"assistant"' in line
            has_err = '"is_error":true' in line or '"is_error": true' in line
            has_result = '"toolUseResult"' in line or '"tool_result"' in line
            if not (has_asst or has_result):
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = d.get("type")
            if t == "assistant":
                m = d.get("message") or {}
                mid = m.get("id")
                cur_model = m.get("model") or cur_model
                if not mid or mid in seen_msgs:
                    continue
                seen_msgs.add(mid)
                u = m.get("usage") or {}
                k = (agent_type, cur_model or "unknown")
                a = acc[k]
                a["msgs"] += 1
                a["output"] += u.get("output_tokens", 0) or 0
                # 計算這則訊息發出的 tool_use 數
                for blk in (m.get("content") or []):
                    if isinstance(blk, dict) and blk.get("type") == "tool_use":
                        a["tool_calls"] += 1
            elif t == "user" and cur_model:
                # tool 結果掛在 user entry;數 is_error
                content = (d.get("message") or {}).get("content")
                if isinstance(content, list):
                    for blk in content:
                        if isinstance(blk, dict) and blk.get("type") == "tool_result":
                            k = (agent_type, cur_model)
                            acc[k]["tool_results"] += 1
                            if blk.get("is_error"):
                                acc[k]["tool_errors"] += 1

def main():
    acc = defaultdict(lambda: {"msgs": 0, "output": 0, "tool_calls": 0, "tool_results": 0, "tool_errors": 0})
    seen = set()
    for proj_dir in sorted(PROJECTS_DIR.iterdir()):
        if not proj_dir.is_dir():
            continue
        project = proj_dir.name.replace("-Users-haosun-", "").replace("Desktop-", "") or "home"
        for f in proj_dir.glob("*.jsonl"):
            scan_file(f, project, "main", acc, seen)
        for agent_file in proj_dir.glob("*/subagents/agent-*.jsonl"):
            meta_file = agent_file.parent / (agent_file.stem + ".meta.json")
            agent_type = "subagent"
            if meta_file.exists():
                try:
                    agent_type = json.load(open(meta_file)).get("agentType") or "subagent"
                except Exception:
                    pass
            scan_file(agent_file, project, agent_type, acc, seen)

    def short(m):
        for k in ("fable-5", "opus", "sonnet", "haiku"):
            if k in m:
                return {"fable-5": "Fable5", "opus": "Opus", "sonnet": "Sonnet", "haiku": "Haiku"}[k]
        return m[:10]

    # 聚合到 (role, model_tier)
    tier = defaultdict(lambda: {"msgs": 0, "output": 0, "tool_results": 0, "tool_errors": 0})
    for (role, model), v in acc.items():
        k = (role, short(model))
        t = tier[k]
        for f in ("msgs", "output", "tool_results", "tool_errors"):
            t[f] += v[f]

    # 持久化:讓 retro_optimize 能 join 成本×品質(每 role::tier 一筆)
    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(exist_ok=True)
    quality_records = {}
    for (role, t), v in tier.items():
        err = v["tool_errors"] / v["tool_results"] if v["tool_results"] else None
        quality_records[f"{role}::{t}"] = {
            "role": role, "tier": t, "msgs": v["msgs"], "output": v["output"],
            "tool_results": v["tool_results"], "tool_errors": v["tool_errors"],
            "error_rate": err,
        }
    (out_dir / "quality.json").write_text(
        json.dumps(quality_records, ensure_ascii=False, indent=1))

    print("== 角色 × 模型層:工作組成與工具錯誤率 (tool_results>=100 才列) ==")
    print(f"{'role':24s} {'tier':7s} {'msgs':>6s} {'out/msg':>8s} {'tool_res':>9s} {'err':>5s} {'err%':>6s}")
    rows = []
    for (role, t), v in tier.items():
        if v["tool_results"] < 100:
            continue
        err = v["tool_errors"] / v["tool_results"] * 100 if v["tool_results"] else 0
        rows.append((role, t, v, err))
    for role, t, v, err in sorted(rows, key=lambda x: (x[0], x[1])):
        print(f"{role:24s} {t:7s} {v['msgs']:>6d} {v['output']//max(v['msgs'],1):>8d} {v['tool_results']:>9d} {v['tool_errors']:>5d} {err:>5.1f}%")

    # 關鍵對照:developer 角色 Sonnet vs Opus
    print("\n== 關鍵對照:同角色不同模型層 (品質代理=工具錯誤率) ==")
    for role in ("developer", "qa", "architect", "main"):
        line = []
        for t in ("Haiku", "Sonnet", "Opus", "Fable5"):
            v = tier.get((role, t))
            if v and v["tool_results"] >= 100:
                line.append(f"{t} {v['tool_errors']/v['tool_results']*100:.1f}% (n={v['tool_results']})")
        if line:
            print(f"  {role:12s}: " + " | ".join(line))

if __name__ == "__main__":
    main()
