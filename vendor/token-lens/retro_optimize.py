#!/usr/bin/env python3
"""token-lens retro_optimize — champion/challenger 晉升引擎(純決策邏輯)。

把一個 sprint 的每格成本×品質,按「三向觸發 → 帕累托規則 + criticality 硬地板」
轉成「晉升提案」。晉升本身不自動套用——寫成提案走 dev-factory 的人類 gate。

品質代理 = 工具錯誤率(越低越好);成本 = 每單位工作成本(越低越好)。
quality = 1 - error_rate。criticality 設一條品質硬地板:高關鍵性禁止拿品質換成本。

用法: python3 retro_optimize.py [seed/sprint-sample.json]
  → 讀該輪每格成本×品質,產出 out/retro-optimize-proposals.md(晉升提案,走人類 gate)。
"""
import json
import sys
from datetime import date
from pathlib import Path

BASE = Path(__file__).parent


# criticality → 品質硬地板 + 是否允許拿品質換成本
CRITICALITY = {
    "low": {"quality_floor": 0.55, "allow_downgrade": True},
    "medium": {"quality_floor": 0.75, "allow_downgrade": True},
    "high": {"quality_floor": 0.90, "allow_downgrade": False},
}


def evaluate(champion, challenger, crit_cfg, min_n=100):
    """比較現任(champion)與挑戰者(challenger),回傳晉升判定。

    champion/challenger: {"model","error_rate","cost","n"}
    crit_cfg: {"quality_floor": 0..1, "allow_downgrade": bool}
    verdict: promote | hold_tradeoff | reject | insufficient_data
    """
    # 1. 樣本不足 → 不憑雜訊晉升
    if challenger.get("n", 0) < min_n:
        return {"verdict": "insufficient_data",
                "reason": f"挑戰者 n={challenger.get('n', 0)} < 門檻 {min_n},證據不足,續觀察"}

    # 2. 必須更便宜才值得換(省成本是目的)
    if challenger["cost"] >= champion["cost"]:
        return {"verdict": "reject",
                "reason": f"挑戰者不更便宜(${challenger['cost']:.3f} ≥ ${champion['cost']:.3f})"}

    # 3. criticality 硬地板:低於品質底線一律拒,不論多便宜
    chal_quality = 1 - challenger["error_rate"]
    if chal_quality < crit_cfg["quality_floor"]:
        return {"verdict": "reject",
                "reason": f"挑戰者品質 {chal_quality:.2f} < 硬地板 {crit_cfg['quality_floor']:.2f}"}

    # 4. 品質不劣化 → 帕累托改善,晉升
    if challenger["error_rate"] <= champion["error_rate"]:
        return {"verdict": "promote",
                "reason": f"更便宜且品質未劣化(err {challenger['error_rate']:.3f} ≤ {champion['error_rate']:.3f}),"
                          f"省 ${champion['cost'] - challenger['cost']:.3f}/單位"}

    # 5. 更便宜但品質較差(仍在地板之上)= trade-off
    if crit_cfg["allow_downgrade"]:
        return {"verdict": "hold_tradeoff",
                "reason": f"更便宜但品質略降(err {challenger['error_rate']:.3f} > {champion['error_rate']:.3f}),"
                          f"低關鍵性可換 → 交人類判"}
    return {"verdict": "reject",
            "reason": f"高關鍵性禁止拿品質換成本(err {challenger['error_rate']:.3f} > {champion['error_rate']:.3f})"}


def detect_triggers(cell, thresholds, cheaper_alt=False):
    """一個 (角色×任務) 格子該不該進優化評估。回傳觸發清單。

    cell: {"cost","error_rate"}
    thresholds: {"cost","error_rate"}
    cheaper_alt: Radar 是否發現同品質層級更便宜的模型(機會觸發)
    """
    triggers = []
    if cell["error_rate"] > thresholds["error_rate"]:
        triggers.append("quality_problem")   # 錯誤變多 → 找更強的挑戰者(升級)
    if cell["cost"] > thresholds["cost"]:
        triggers.append("cost_problem")       # 支出過高 → 找更便宜的挑戰者(降級)
    if cheaper_alt:
        triggers.append("radar_opportunity")  # 市場出現更划算的選項 → 主動挑戰
    return triggers


def pick_challenger(champion_model, intel, trigger, quality_floor):
    """從 Radar 情報選一個挑戰者模型。

    成本/機會觸發 → 便宜於現任、且品質先驗仍在硬地板之上的最便宜者(最大膽的安全降層)。
    品質觸發 → 品質先驗高於現任的最便宜者(用最小代價脫離品質問題)。
    找不到合適者回傳 None。
    """
    champ = next((r for r in intel if r["model"] == champion_model), None)
    if trigger == "quality_problem":
        champ_q = champ["quality_prior"] if champ else 0.0
        cands = [r for r in intel if r["quality_prior"] > champ_q]
    else:  # cost_problem / radar_opportunity
        champ_price = champ["price"] if champ else float("inf")
        cands = [r for r in intel
                 if r["price"] < champ_price and r["quality_prior"] >= quality_floor]
    if not cands:
        return None
    return min(cands, key=lambda r: r["price"])["model"]


def build_proposals(cells, intel, thresholds, min_n=100):
    """把一輪 sprint 的每格 → 晉升/挑戰提案清單。純函數,不寫檔。

    cell: {"key","model","cost","error_rate","n","criticality",
           "challenger"?: {"model","cost","error_rate","n"}}
    每格:偵測觸發 → 有挑戰者實測資料就 evaluate 出判定;否則選一個挑戰者提出實驗。
    """
    proposals = []
    for cell in cells:
        crit = CRITICALITY[cell["criticality"]]
        cheaper_alt = pick_challenger(
            cell["model"], intel, "cost_problem", crit["quality_floor"]) is not None
        triggers = detect_triggers(
            {"cost": cell["cost"], "error_rate": cell["error_rate"]}, thresholds, cheaper_alt)
        if not triggers:
            continue
        if cell.get("challenger"):
            v = evaluate({"model": cell["model"], "error_rate": cell["error_rate"],
                          "cost": cell["cost"], "n": cell["n"]},
                         cell["challenger"], crit, min_n)
            proposals.append({"kind": "evaluate", "key": cell["key"],
                              "champion": cell["model"], "challenger": cell["challenger"]["model"],
                              "verdict": v["verdict"], "reason": v["reason"], "triggers": triggers})
        else:
            trig = "quality_problem" if "quality_problem" in triggers else "cost_problem"
            chal = pick_challenger(cell["model"], intel, trig, crit["quality_floor"])
            if chal:
                proposals.append({"kind": "challenge", "key": cell["key"],
                                  "champion": cell["model"], "challenger": chal,
                                  "triggers": triggers})
            else:
                proposals.append({"kind": "no_candidate", "key": cell["key"],
                                  "champion": cell["model"], "triggers": triggers})
    return proposals


# ──────────────────────────── I/O 層(glue)────────────────────────────

def load_thresholds(path=BASE / "thresholds.txt"):
    """讀 thresholds.txt → {'cost': USD, 'error_rate': fraction}。"""
    cost, err_pct = 3.0, 8.0
    p = Path(path)
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if line.startswith("sprint_cost_usd="):
                cost = float(line.split("=", 1)[1])
            elif line.startswith("role_tool_error_pct="):
                err_pct = float(line.split("=", 1)[1])
    return {"cost": cost, "error_rate": err_pct / 100}


def render(proposals, sprint):
    kind_label = {"challenge": "🧪 提出挑戰實驗", "evaluate": "⚖️ 評估已完成挑戰",
                  "no_candidate": "🚫 無合適挑戰者"}
    verdict_label = {"promote": "✅ 晉升(寫回建議表)", "hold_tradeoff": "🤝 trade-off(交人類判)",
                     "reject": "❌ 維持現任", "insufficient_data": "⏳ 證據不足,續觀察"}
    lines = [f"# retro_optimize 晉升提案 — sprint `{sprint}` ({date.today()})", "",
             "> 引擎產出,**非自動套用**。晉升 = 對建議表的政策變更,須人類核可後才寫回 "
             "`router-policy.yaml`(與 dev-factory retro 的核可線一致)。", ""]
    if not proposals:
        lines.append("本輪無觸發,建議表維持現狀。")
        return "\n".join(lines) + "\n"
    for p in proposals:
        lines.append(f"## `{p['key']}` — {kind_label[p['kind']]}")
        lines.append(f"- 觸發:{', '.join(p['triggers'])}")
        lines.append(f"- 現任:`{p['champion']}`")
        if p["kind"] == "challenge":
            lines.append(f"- 建議挑戰者:`{p['challenger']}`(下輪 shadow/canary 跑,回來再 evaluate)")
        elif p["kind"] == "evaluate":
            lines.append(f"- 挑戰者:`{p['challenger']}` → **{verdict_label[p['verdict']]}**")
            lines.append(f"- 理由:{p['reason']}")
        else:
            lines.append("- Radar 中無同品質層級更便宜的候選;維持現任。")
        lines.append("")
    promotes = [p for p in proposals if p.get("verdict") == "promote"]
    lines.append(f"---\n**待核可晉升 {len(promotes)} 筆** / 提案共 {len(proposals)} 筆。"
                 "核可後由人類更新建議表——引擎不自己改。")
    return "\n".join(lines) + "\n"


def main():
    seed = sys.argv[1] if len(sys.argv) > 1 else str(BASE / "seed" / "sprint-sample.json")
    data = json.loads(Path(seed).read_text())
    intel = json.loads((BASE / "model-intel.json").read_text())["models"]
    thresholds = load_thresholds()
    proposals = build_proposals(data["cells"], intel, thresholds)
    out = BASE / "out" / "retro-optimize-proposals.md"
    out.parent.mkdir(exist_ok=True)
    md = render(proposals, data.get("sprint", "?"))
    out.write_text(md)
    print(md)


if __name__ == "__main__":
    main()
