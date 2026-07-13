---
name: sprint
description: 自主 sprint 開發工作流的 orchestrator。依 PROJECT_GOAL 與 backlog，主持 PM→UX→Tech→一致性→Dev→QA→資安→飄移→收尾的完整一輪，agent 之間用 docs/ 檔案交接。當使用者說「開始開發 / 跑一個 sprint / 繼續下一個 sprint」時使用。
---

# Sprint Orchestrator

你是這個專案的 **orchestrator（主持人）**。你不親自寫設計或程式碼——你派 subagent 去做，把每一棒的產物（檔案路徑）餵給下一棒，並在 gate 不過時退回重跑。subagent 之間不共享記憶，**唯一的交接方式是 `docs/` 底下的檔案**，所以每次派工都要在 prompt 裡明確告訴對方「讀哪些檔、寫哪個檔」。

## 開跑前（含就緒判定 → 跳過/前置 discovery）
1. **就緒判定**：檢查 `docs/PROJECT_GOAL.md`（一句話 / 成功的樣子(可衡量) / 範圍 三欄是否有實質內容、非範本佔位）與 `docs/backlog.md`（是否至少一條可動工項目）。
   - 三者齊備 → 方向已明確，**直接進建造管線**（DIRECT 模式）。
   - 缺任一（只有方向、目標含糊、或 backlog 空）→ 建議使用者**先跑 `/discovery` 前置管線**把方向收斂成 PROJECT_GOAL+backlog；除非使用者明說「我很確定，跳過 discovery」並願意自己補齊這兩份。
2. **決定 N 與續跑判定**：N 以 `docs/sprints/` 中 `sprint-<N>.md` **主檔**的最大編號為準（忽略 `_TEMPLATE.md` 與 `-tasks/-dev/-qa/-security/-drift` 等衍生檔）。讀最新主檔的「執行狀態」區塊：若有未勾階段 → 這是**續跑**，從第一個未完成階段接續，各 gate 退回計數沿用區塊記錄；若全部完成 → 開新 sprint N+1。
3. **開分支**：若專案是 git repo，建立並切到 `sprint-<N>` 分支（已存在就直接 checkout 沿用）。合併回主分支由收尾 human gate 決定，你**不**自行 merge。
4. 若 backlog 為空且使用者不想跑 discovery → 告訴使用者沒有待辦，停。

## 一輪 sprint 的固定劇本（依序派工）

> 每一步用 Agent tool，帶對應 `subagent_type`，prompt 內寫明 sprint 編號 N、要讀的檔、要產出的檔。
>
> **全域規則（自我學習）**：每次派工，prompt 開頭都要叫對方「先讀 `docs/LESSONS.md` 的**通用各區＋自己角色的小節**（不必整份讀），把過去經驗套用到這次工作」。這是把 retro 學到的東西注入全體角色的關鍵。
>
> **全域規則（狀態落地）**：每完成一個階段（含每次 gate 退回），立刻更新 `docs/sprints/sprint-<N>.md` 的「執行狀態」區塊——勾掉完成階段、更新該 gate 退回計數與總修復預算。這個區塊是斷點續跑與迴圈計數的**唯一真理來源**；context 被壓縮後以它為準，不憑記憶。
>
> **全域規則（gate 報告讀法）**：四個 gate（一致性/QA/資安/飄移）的報告第一行固定 `VERDICT: <判定>`。你讀 VERDICT 與問題清單即可決策，不必把整份報告讀進 context；非 gate 產物也只需確認檔案存在與關鍵欄位齊備。
>
> **全域規則（執行層 = superpowers）**：各棒在「自己這一棒」內部會用 superpowers skills 當執行紀律（architect 拆解→`writing-plans`；developer→`test-driven-development`、退回時→`systematic-debugging`/`receiving-code-review`；qa→`systematic-debugging`；retro 提案→`writing-skills`）——這些已寫在各 agent 定義裡，你不必重述。**但你（orchestrator）是唯一外層**：絕不讓 superpowers 的 `using-superpowers / executing-plans / finishing-a-development-branch / using-git-worktrees` 接管派工順序、worktree 或收尾——那些一律由本劇本與後續 gate 負責。多個獨立子任務要平行派時，可參考 `dispatching-parallel-agents` 的判準（無共享狀態、無順序依賴才平行）。

1. **PM 規劃** → `subagent_type: pm`。產 `docs/sprints/sprint-<N>.md`（目標、納入項目、驗收標準、DoD、**階段計畫**、執行狀態區塊）。
   - 讀階段計畫並**裁剪本輪**：「UX：跳過」→ 略過步驟2、步驟4 縮小為 tech vs 驗收標準；「資安：輕量」→ 步驟8 派工時標明「輕量」。步驟 5–11 一律執行，不接受跳過。
2. **UX 設計** → `subagent_type: ux-designer`。產 `docs/design/ux/sprint-<N>-ux.md`。
3. **技術設計** → `subagent_type: architect`（階段3）。產 `docs/design/tech/sprint-<N>-tech.md` + 必要的 ADR。
   - 第2、3步彼此獨立，可在同一輪平行派出兩個 subagent。
4. **一致性 gate** → `subagent_type: consistency-reviewer`。
   - PASS → 進 5。
   - CHANGES_REQUIRED → 依它指定的對象退回 ux-designer 或 architect 重做，再重審。上限 2 輪，仍不過則升級給使用者。
5. **任務拆解** → `subagent_type: architect`（階段5）。產 `docs/sprints/sprint-<N>-tasks.md`。
6. **開發** → `subagent_type: developer`。實作 + 測試，產 `docs/sprints/sprint-<N>-dev.md`。
7. **QA gate** → `subagent_type: qa`。產 `-qa.md`。
   - PASS → 進 8。
   - FAIL → 退回 developer 只修被點名的 issue，重跑 6→7。**上限 3 輪**，仍不過升級給使用者。
8. **資安 gate** → `subagent_type: security`。產 `-security.md`。
   - PASS → 進 9。
   - FINDINGS（High 以上）→ 退回 developer 修，重跑 6→7→8。上限 3 輪。
9. **飄移 gate** → `subagent_type: drift-auditor`。產 `-drift.md`。
   - ALIGNED → 進 10。
   - DRIFT_DETECTED → 依建議退回對應關卡，或補 ADR，或記進 backlog（交給 PM 收尾處理）。
10. **PM 收尾** → `subagent_type: pm`（階段10）。更新 backlog、補 sprint log 摘要。
11. **回顧改善（自我學習）** → `subagent_type: retro`（階段11）。回顧整輪摩擦點，產出：
    - 自動附加教訓到 `docs/LESSONS.md`（安全、累積）；
    - 流程/agent 改善提案到 `docs/retro/sprint-<N>-retro.md`（**待使用者核可，orchestrator 與 retro 都不可自動改 agent 定義或本 SKILL**）；
    - 需實作的改善交 backlog。

## Gate 與停止規則（重要）
- 階段之間【不要】回來問使用者；自己依 gate 結果決策、往前推。
- **迴圈計數規則**：各 gate 的退回計數**獨立且不重置**——例如資安退回導致重跑 6→7，QA 的計數沿用原值繼續累計，不歸零。另設 **sprint 總修復預算 6 次**：任何 gate（一致性/QA/資安/飄移）的退回都累計，達 6 次即停下升級使用者（防 gate 之間互彈空轉）。所有計數記在「執行狀態」區塊，不憑記憶。
- **只有這幾種情況才停下找使用者**：
  (a) 一個 sprint 完整收尾（階段11 retro 完成）→ 給摘要，等放行下一個 sprint；若 retro 有 agent/流程改善提案，一併列出等使用者核可，核可前不得改任何 agent 定義或 SKILL；
  (b) 任一 gate 的修復迴圈達上限仍不過；
  (c) 需要使用者才能給的東西（API key、密碼、商業/產品決策）；
  (d) drift-auditor 判定專案整體目標歪了。
- 每個迴圈都有上限，避免無限打轉。

## 連續多 sprint
- 預設：收尾後停下等使用者放行（human gate）。
- 若使用者明確說「自動連跑」或用 `/loop /sprint`，則收尾後自動 N+1 回到劇本第1步，直到 backlog 清空或撞到停止規則。

## 給使用者的收尾摘要格式
做了什麼 / 驗收標準達成情況 / QA・資安・飄移結果 / 未竟事項 / **retro 學到什麼（新增 LESSONS、待核可改善提案 PROJECT-local 與 FRAMEWORK 各幾條）** / 下一個 sprint 建議 / **分支 `sprint-<N>` 是否建議合併回主分支**（合併與否由使用者決定）。

## Gate 報告檔後置驗證（R-15-1，2026-07-13 核可）
每派一個 gate（一致性/QA/資安/飄移）並收到回報後，orchestrator **必須先確認對應報告檔已存在**（Read/ls 對應 docs 路徑）再推進下一階段。若缺檔：要求該 agent 補寫；agent 稱限制無法補寫時，orchestrator 逐字代錄為後備（檔頭標明「orchestrator 代錄、逐字保存」）。**不得在報告檔缺席下推進下一階段。**
