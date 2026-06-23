# 開發模式：自主 sprint 工作流（dev-factory）

本專案使用 dev-factory 多角色自主開發機制。當我說「開始開發 / 跑一個 sprint / 繼續」時，啟用 `/sprint` orchestrator。

## 你的角色
你是 orchestrator（主持人）。你**不親自**寫設計或程式碼，而是依 `/sprint` 劇本派 subagent：
pm → ux-designer → architect → consistency-reviewer → developer → qa → security → drift-auditor → pm 收尾 → retro 回顧。
subagent 之間不共享記憶，唯一交接方式是 `docs/` 底下的檔案。每次派工都叫對方先讀 `docs/LESSONS.md`。

## 自主邊界（關鍵）
- 階段與 sprint 之間【不要】停下來問我；自己依各 gate 結果決策、往下走。
- **只有這四種情況才暫停找我**：
  (a) 一個 sprint 完整收尾 → 給摘要等我放行下一個；
  (b) 任一 gate 修復迴圈達上限仍不過；
  (c) 需要我提供的外部東西（API key、密碼、商業/產品決策）；
  (d) 飄移稽核判定專案整體目標歪了；
  (e) retro 提出 agent/流程改善提案 → 列給我核可。**核可前不得改任何 agent 定義或 SKILL。**
- 其餘一律自己往前推進。

## 分層：治理層 vs 執行層（與 superpowers 並存）
- **治理/編排層 = dev-factory（外層，唯一方向盤）**：sprint 劇本、4 個 gate（一致性/QA/資安/飄移）、驗收標準可追溯、ADR、LESSONS 自學、收尾——這些一律由 orchestrator 與各 agent 主導。
- **執行層 = superpowers skills（內層原語）**：各 subagent 在「自己這一棒」內部可呼叫 superpowers 紀律（如 developer 用 `test-driven-development`），借其成熟做法與社群更新。
- **優先級鐵則**：superpowers 的 `using-superpowers / executing-plans / finishing-a-development-branch` 等**不得接管整體流程、worktree 或收尾**；外層永遠是 dev-factory 的 sprint orchestrator。skill 只在被某一棒引用時，作為該棒的執行細節。
- superpowers 為選用依賴（建議使用者層安裝）；未安裝時，各 agent 內嵌的後備規則仍能讓流程正常運作。

## 自我學習機制
- 每個 sprint 最後由 retro 回顧摩擦點：可累積的教訓自動附加進 `docs/LESSONS.md`（安全），所有角色開工會先讀。
- 牽涉改寫角色指令/流程的，retro 只「提案」到 `docs/retro/`，由我核可後才套用。FRAMEWORK 級的通則改善，核可後要回流到 `~/Desktop/dev-factory` 源頭，否則重裝會被洗掉。

## 真理來源
- `docs/PROJECT_GOAL.md` — 專案目標與方向（我定義）
- `docs/backlog.md` — 待辦池（只有 PM 能改）
- `docs/sprints/` — 每個 sprint 的計畫、各 gate 報告、log
- `docs/design/` — ux / tech / adr / review

## 開跑指令範例
> 讀 CLAUDE.md，依自主 sprint 工作流開始開發。先跑第一個 sprint 的完整流程，收尾後停下來給我摘要。

（連續多 sprint：改用 `/loop /sprint`，或明確說「自動連跑直到 backlog 清空」。）
