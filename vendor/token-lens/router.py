#!/usr/bin/env python3
"""token-lens Router — 依「任務 × criticality」派工到模型。

決策來自版本化的建議表(router-policy.yaml 的 routes 段);表裡沒有的冷格,
退回 Radar 先驗(model-intel.json):在該 criticality 的品質硬地板之上選最便宜者。
建議表由 retro_optimize 的晉升提案經人類核可後更新——Router 不自己學,只查表 + 冷啟動兜底。
"""
import json
import sys
from pathlib import Path

from retro_optimize import CRITICALITY

BASE = Path(__file__).parent
INTEL_FILE = BASE / "model-intel.json"


def load_intel(path=INTEL_FILE):
    data = json.loads(Path(path).read_text())
    return data["models"]


def route(task_type, criticality, policy, intel):
    """回傳 {model, effort, source, rationale}。source ∈ policy | cold_start_prior。"""
    key = f"{task_type}:{criticality}"
    routes = policy.get("routes", {})
    if key in routes:
        r = routes[key]
        return {"model": r["model"], "effort": r.get("effort"),
                "source": "policy", "rationale": r.get("evidence", "建議表命中")}
    # 冷啟動:採 Radar 先驗
    floor = CRITICALITY[criticality]["quality_floor"]
    cands = [m for m in intel if m["quality_prior"] >= floor]
    if not cands:
        return {"model": None, "effort": None, "source": "cold_start_prior",
                "rationale": f"無模型達 {criticality} 地板 {floor}"}
    pick = min(cands, key=lambda m: m["price"])
    return {"model": pick["model"], "effort": None, "source": "cold_start_prior",
            "rationale": f"冷啟動:{criticality} 地板 {floor} 之上最便宜者(待 retro 用實測覆蓋)"}


def _parse_routes(text):
    """解析 router-policy.yaml 的 routes 段(list-of-dict,手解析,不依賴 PyYAML)。

    routes:
      - key: code:medium
        model: sonnet   # 可帶行內註解
        effort: high
    """
    def val(s):  # 取 ':' 後的值並剝掉行內註解
        return s.split(":", 1)[1].split("#", 1)[0].strip()

    in_routes = False
    entries = []
    cur = None
    for line in text.splitlines():
        if line.rstrip() == "routes:":
            in_routes = True
            continue
        if in_routes:
            if line and not line[0].isspace():
                break  # 回到頂層 key,routes 段結束
            s = line.strip()
            if s.startswith("- key:"):
                cur = {"key": s[len("- key:"):].split("#", 1)[0].strip()}
                entries.append(cur)
            elif cur and s.startswith("model:"):
                cur["model"] = val(s)
            elif cur and s.startswith("effort:"):
                cur["effort"] = val(s)
    return {e["key"]: {"model": e.get("model"), "effort": e.get("effort")}
            for e in entries if "model" in e}


def _load_policy():
    pf = BASE / "router-policy.yaml"
    if not pf.exists():
        return {"routes": {}}
    return {"routes": _parse_routes(pf.read_text())}


def main():
    if len(sys.argv) < 3:
        print("用法: python3 router.py <task_type> <low|medium|high>", file=sys.stderr)
        sys.exit(1)
    task, crit = sys.argv[1], sys.argv[2]
    r = route(task, crit, _load_policy(), load_intel())
    print(f"{task} × {crit} → {r['model']} (effort={r['effort']}) "
          f"[{r['source']}] {r['rationale']}")


if __name__ == "__main__":
    main()
