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
2. **治理 profile 判定（HUMAN GATE，每專案問一次）**：讀 `docs/PROJECT_GOAL.md` 是否已有「治理 profile：lean / standard / max」欄位。
   - **已設** → 沿用，不再問；整輪劇本依它裁剪。
   - **未設** → 評估專案規模與風險（backlog 量、是否有 UI、是否碰 auth/金流/敏感資料、上線產品 vs 原型），**建議一個 profile 並附一句理由，停下問使用者**。使用者選定後把該欄位代寫進 `docs/PROJECT_GOAL.md`，之後該專案固定用它。三種 profile：
     - **`lean`**（原型 / solo / 內部工具，最省）：單一 `reviewer` 合併驗證關（功能+資安+飄移一棒）；一致性折進 architect 自檢；UX 僅在有可見面時跑。約 5 棒 / sprint。
     - **`standard`**（多數正式專案）：QA 獨立一棒 + `reviewer` 合併（資安+飄移）；有可見面才跑 UX + 獨立一致性 gate；PM 可單輪標「拆資安」。
     - **`max`**（高風險 / 上線 / 合規）：QA / 資安 / 飄移**全拆**專家棒；UX + 獨立一致性一律保留。最嚴最貴。
   - 使用者說「不用問、給我最省」→ 逕用 `lean`；「照舊」→ 用 `standard`。
3. **UX 強度判定（同一次 HUMAN GATE，每專案問一次）**：讀 `docs/PROJECT_GOAL.md` 是否已有「UX 強度：light / full」欄位。
   - **已設** → 沿用，不再問。
   - **未設** → **與 profile 同一次問**（不要分兩次打擾使用者）。依專案是否以 UI 為主要價值來源建議一個：
     - **`light`**（預設）：純後端/CLI/資料專案，或 UI 只是薄殼、品質不是重點。＝現行行為。
     - **`full`**：UI 品質是產品成敗關鍵（面向終端使用者的產品、行銷頁、需要「看起來專業」的東西）。啟用設計系統硬約束 + S5.5 視覺關。**成本**：多一棒 opus 視覺關 + 可能的退回迴圈。
   - 選定後把該欄位代寫進 `docs/PROJECT_GOAL.md`。**與治理 profile 正交**——profile 管 gate 嚴格度，UX 強度管 UX 深度，兩者互不決定對方（內部工具可以 lean + full；後端服務可以 max + light）。
   - 若選 `full`，順帶確認 PROJECT_GOAL 的「技術約束 → 預覽指令」有填；沒填就一起問（visual-reviewer 靠它起專案；缺了視覺關只能回 SKIPPED）。
4. **決定 N 與續跑判定**：N 以 `docs/sprints/` 中 `sprint-<N>.md` **主檔**的最大編號為準（忽略 `_TEMPLATE.md` 與 `-tasks/-dev/-review/-visual/-qa/-security/-drift` 等衍生檔）。讀最新主檔的「執行狀態」區塊：若有未勾階段 → 這是**續跑**，從第一個未完成階段接續，各 gate 退回計數沿用區塊記錄；若全部完成 → 開新 sprint N+1。
5. **開分支**：若專案是 git repo，建立並切到 `sprint-<N>` 分支（已存在就直接 checkout 沿用）。合併回主分支由收尾 human gate 決定，你**不**自行 merge。
6. 若 backlog 為空且使用者不想跑 discovery → 告訴使用者沒有待辦，停。

## 一輪 sprint 的固定劇本（依序派工）

> 每一步用 Agent tool，帶對應 `subagent_type`，prompt 內寫明 sprint 編號 N、要讀的檔、要產出的檔。
>
> **全域規則（自我學習）**：每次派工，prompt 開頭都要叫對方「先讀 `docs/LESSONS.md` 的**通用各區＋自己角色的小節**（不必整份讀），把過去經驗套用到這次工作」。這是把 retro 學到的東西注入全體角色的關鍵。
>
> **全域規則（狀態落地）**：每完成一個階段（含每次 gate 退回），立刻更新 `docs/sprints/sprint-<N>.md` 的「執行狀態」區塊——勾掉完成階段、更新該 gate 退回計數與總修復預算。這個區塊是斷點續跑與迴圈計數的**唯一真理來源**；context 被壓縮後以它為準，不憑記憶。
>
> **全域規則（gate 報告讀法）**：所有 gate（一致性/合併 reviewer/QA/資安/飄移）的報告第一行固定 `VERDICT: <判定>`。你讀 VERDICT 與問題清單即可決策，不必把整份報告讀進 context；非 gate 產物也只需確認檔案存在與關鍵欄位齊備。
>
> **全域規則（窄 context 退回，省 token）**：任何 gate 退回 developer 時，派工 prompt 必附「**本輪只需碰：<gate 點名的檔案清單>；不要重新探索整個 codebase**」。退回是定點修，不是重來。
>
> **全域規則（執行層 = superpowers）**：各棒在「自己這一棒」內部會用 superpowers skills 當執行紀律（architect 拆解→`writing-plans`；developer→`test-driven-development`、退回時→`systematic-debugging`/`receiving-code-review`；qa→`systematic-debugging`；retro 提案→`writing-skills`）——這些已寫在各 agent 定義裡，你不必重述。**但你（orchestrator）是唯一外層**：絕不讓 superpowers 的 `using-superpowers / executing-plans / finishing-a-development-branch / using-git-worktrees` 接管派工順序、worktree 或收尾——那些一律由本劇本與後續 gate 負責。多個獨立子任務要平行派時，可參考 `dispatching-parallel-agents` 的判準（無共享狀態、無順序依賴才平行）。

> **劇本隨 profile 伸縮**：以下是 **standard** 的完整劇本。開跑前判定的 profile 決定裁剪：`lean` 折疊一致性 + 合併驗證關成單一 reviewer；`max` 保留獨立一致性 + 全拆 QA/資安/飄移。每步標了各 profile 的差異。

**S1. PM 規劃** → `subagent_type: pm`。產 `docs/sprints/sprint-<N>.md`（目標、納入項目、驗收標準、DoD、**階段計畫**、執行狀態區塊）。
   - 讀階段計畫並**裁剪本輪**：
     - 「使用者可見面：無」→ 略過 S2（UX）、且 S4 獨立一致性 gate **折進 architect 自檢**（不另派 consistency-reviewer）。
     - profile=`lean` → 一律折疊 S4（不論有無可見面，一致性都進 architect 自檢）。
     - PM 標「本輪資安：拆獨立棒＋完整」→ S6 驗證關把資安拆成獨立 `security` 棒做滿。
   - S5–S8 一律執行，不接受跳過。

**S2. UX 設計**（有使用者可見面才跑）→ `subagent_type: ux-designer`。產 `docs/design/ux/sprint-<N>-ux.md`。
   - UX 強度=`full` → 派工 prompt 標明「**本專案 UX 強度=full：`docs/design/design-system.md` 是硬約束，只能用它既有的 token 與元件；缺的標 `⚠️ 需擴充 design system`**」。

**S3. 架構（設計 + 拆解，**一棒融合**）** → `subagent_type: architect`。**同一次 dispatch** 連續產 `docs/design/tech/sprint-<N>-tech.md`（+ 必要 ADR）與 `docs/sprints/sprint-<N>-tasks.md`——不要分兩次派（省一次冷啟動重讀 codebase）。
   - 派工時若本輪折疊一致性（lean 或無可見面），prompt 標明「**一致性 gate 折疊本棒自檢**」，architect 會在 tech 檔尾附「一致性自檢結論」。
   - S2、S3 彼此獨立，有 UX 時可同一輪平行派出兩個 subagent。

**S4. 一致性 gate**（standard 有可見面 / max 才派）→ `subagent_type: consistency-reviewer`。產 `docs/design/review/sprint-<N>-consistency.md`。
   - PASS → 進 S5。CHANGES_REQUIRED → 依指定對象退回 ux-designer 或 architect 重做再重審。**上限 2 輪**，仍不過升級使用者。
   - （lean / 無可見面：本步已折進 S3 architect 自檢，跳過。）

**S5. 開發** → `subagent_type: developer`。實作 + 測試，產 `docs/sprints/sprint-<N>-dev.md`。

**S5.5 視覺關**（`UX 強度=full` **且**本輪有使用者可見面才派）→ `subagent_type: visual-reviewer`。產 `docs/sprints/sprint-<N>-visual.md`。
   - 派工 prompt 要給：sprint 編號 N、預覽指令（取自 PROJECT_GOAL）、要讀的檔（`design-system.md`、`sprint-<N>-ux.md`、`sprint-<N>.md`）、要寫的檔。
   - `PASS` → 進 S6。
   - `CHANGES_REQUIRED` → 窄 context 退回 developer（附報告點名的檔案清單），修完重跑 S5.5。**上限 2 輪**，仍不過升級使用者。
   - `SKIPPED`（起不來/缺預覽指令）→ **不擋關，直接進 S6**，但要把原因記進「執行狀態」區塊，並在收尾摘要告訴使用者「本輪視覺關未執行，原因：<…>」。連續兩個 sprint SKIPPED → 收尾時建議使用者修好預覽指令，否則 Track B 形同虛設。
   - UX 強度=`light`，或本輪無使用者可見面 → 跳過本步（不派）。

**S6. 驗證關（形態依 profile）** — 這是 P0-1 合併點：
   - **`lean`** → 單一 `subagent_type: reviewer`，派工標「**本輪涵蓋：功能, 資安, 飄移**」。產 `docs/sprints/sprint-<N>-review.md`。
     - PASS → 進 S7。CHANGES_REQUIRED → 依報告分區塊處置：功能/資安退回 developer（窄 context）、飄移補 ADR 或記 backlog。重跑 S5→S6。
   - **`standard`** →
     a. `subagent_type: qa` 先跑（功能/回歸）→ 產 `-qa.md`。FAIL → 退回 developer 重跑 S5→(a)。
     b. QA PASS 後派 `subagent_type: reviewer` 標「**本輪涵蓋：資安, 飄移**」→ 產 `-review.md`（功能區塊註明「由 QA 負責」）。
        - 若 PM 標「拆資安」→ 改派 `subagent_type: security`（完整）+ reviewer 標「本輪涵蓋：飄移」（或直接 `subagent_type: drift-auditor`）。
        - CHANGES_REQUIRED（資安 High 以上 / 飄移需退回）→ 退回 developer 或補 ADR/記 backlog，重跑。
   - **`max`** → 依序 `qa` → `security` → `drift-auditor` 三獨立棒（原經典流程），各產 `-qa.md`/`-security.md`/`-drift.md`。任一不過退回 developer 重跑。
   - **迴圈上限**：驗證關整體退回 developer **上限 3 輪**；飄移類「補 ADR / 記 backlog」不計退回。

**S7. PM 收尾（瘦身）** → `subagent_type: pm`。**只讀驗證關報告的 VERDICT 與待辦清單**（不重驗 AC），更新 backlog、補 sprint log 摘要。

**S8. 回顧改善（自我學習）** → `subagent_type: retro`。回顧整輪摩擦點，產出：
    - 自動附加教訓到 `docs/LESSONS.md`（安全、累積）；
    - 流程/agent 改善提案到 `docs/retro/sprint-<N>-retro.md`（**待使用者核可，orchestrator 與 retro 都不可自動改 agent 定義或本 SKILL**）；
    - 需實作的改善交 backlog。

## Gate 與停止規則（重要）
- 階段之間【不要】回來問使用者；自己依 gate 結果決策、往前推。
- **迴圈計數規則**：各 gate 的退回計數**獨立且不重置**（一致性 2 / **視覺關 2** / 驗證關 3）。另設 **sprint 總修復預算 6 次**：任何 gate（一致性/視覺關/驗證關各區塊）的退回都累計，達 6 次即停下升級使用者（防 gate 之間互彈空轉）。所有計數記在「執行狀態」區塊，不憑記憶。
- **只有這幾種情況才停下找使用者**：
  (a) 一個 sprint 完整收尾（S8 retro 完成）→ 給摘要，等放行下一個 sprint；若 retro 有 agent/流程改善提案，一併列出等使用者核可，核可前不得改任何 agent 定義或 SKILL；
  (b) 任一 gate 的修復迴圈達上限仍不過；
  (c) 需要使用者才能給的東西（API key、密碼、商業/產品決策）；
  (d) 驗證關（reviewer 飄移區塊 / drift-auditor）判定專案整體目標歪了。
- 每個迴圈都有上限，避免無限打轉。

## 連續多 sprint
- 預設：收尾後停下等使用者放行（human gate）。
- 若使用者明確說「自動連跑」或用 `/loop /sprint`，則收尾後自動 N+1 回到劇本第1步，直到 backlog 清空或撞到停止規則。

## 給使用者的收尾摘要格式
做了什麼 / 驗收標準達成情況 / 驗證關結果（功能・資安・飄移） / **視覺關結果（PASS/SKIPPED＋原因）** / 未竟事項 / **retro 學到什麼（新增 LESSONS、待核可改善提案 PROJECT-local 與 FRAMEWORK 各幾條）** / 下一個 sprint 建議 / **分支 `sprint-<N>` 是否建議合併回主分支**（合併與否由使用者決定）。

## Gate 報告檔後置驗證（R-15-1，2026-07-13 核可）
每派一個 gate（一致性/**視覺關**/合併 reviewer/QA/資安/飄移）並收到回報後，orchestrator **必須先確認對應報告檔已存在**（Read/ls 對應 docs 路徑：`-review.md` / `-consistency.md` / `-visual.md` / `-qa.md` / `-security.md` / `-drift.md`）再推進下一階段。若缺檔：要求該 agent 補寫；agent 稱限制無法補寫時，orchestrator 逐字代錄為後備（檔頭標明「orchestrator 代錄、逐字保存」）。**不得在報告檔缺席下推進下一階段。**
