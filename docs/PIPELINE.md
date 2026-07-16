# dev-factory 開發流程（PIPELINE）

整套有兩段：**discovery 前置管線（選用）** 把模糊方向收斂成目標，**建造管線（/sprint）** 把目標蓋成軟體。已經很確定要做什麼，可直接跳過 discovery 進建造。

```
  只有方向 ──/discovery──► PROJECT_GOAL+backlog ─┐
                                                 ├──/sprint──► 可運作的軟體
  已有明確目標 ────────────────────────────────┘
            （就緒判定：目標三欄齊備且 backlog 非空 → 直接建造；否則建議先 discovery）
```

## 前置：discovery 管線（選用，可跳過）

沒有具體構想、只給方向時用。發散 → 證據式批判驗證（迴圈）→ 收斂，agent 給你建議並反覆驗證，最後產出建造管線要的入口檔。

```
 docs/DIRECTION.md（你只填方向、約束、不確定的問題）
        │  /discovery
        ▼
 D1. explorer 發散 3–5 概念 ◄────────────┐
        │ （各標「最關鍵待驗證假設」）     │ REFINE（退回精修）
        ▼                                │
 D2. critic 證據式驗證 (gate) ───────────┘ 依 rubric 評分，迴圈上限 3 輪
        │ KILL/REFINE/PROMOTE              達上限無 PROMOTE → 升級：建議調整 DIRECTION
        ▼ ≥1 PROMOTE
 D3. recommendation ──[HUMAN GATE] 你挑一個 / 全否換方向
        ▼
 D4. shaper → docs/PROJECT_GOAL.md + docs/backlog.md
        ▼
   [HUMAN GATE] 核可後 ──► 進建造管線 /sprint
```

| 階段 | 角色 | 產物 | gate? |
|------|------|------|-------|
| D1 | explorer | `discovery/concepts.md`（3–5 候選概念） | |
| D2 | critic | `discovery/validation-<r>.md` → `discovery/recommendation.md` | ✅ (≤3輪) |
| D3 | —（使用者挑選） | — | 🧑 human |
| D4 | shaper | `PROJECT_GOAL.md` + `backlog.md` | 🧑 human |

**驗證判準**（`discovery/rubric.md`，權重可由使用者編輯）：有人要嗎(desirability) / 做得出來嗎(feasibility) / 值得做嗎(viability) / 能便宜驗證嗎(validatability)，預設各 25%。critic 鎖定每個概念自己的關鍵假設、用 WebSearch 找證據評分，**禁止憑感覺**。discovery 也可單獨跑（只要建議、不一定往下建造，停在 D3）。

---

## 建造管線（/sprint）

一輪 sprint 的邏輯階段 S1–S8。每關是 **agent gate**（不過退回上一棒重跑，不打擾使用者），只有 sprint 收尾（retro 之後）是 **human gate**。

**流程隨「治理 profile」伸縮**（開跑首次問一次、每專案固定）——這是控制時間/token 成本的主鈕：
- **lean**：驗證關合併成**單一 reviewer**（功能+資安+飄移一棒）、一致性折進 architect 自檢、UX 僅有可見面才跑。約 5 棒。
- **standard**：QA 獨立 + reviewer 合併（資安+飄移）、有可見面才跑 UX+獨立一致性。
- **max**：QA/資安/飄移全拆專家棒、UX+一致性一律保留。

**另有正交的「UX 強度」開關**（light/full，同樣每專案問一次）：`full` 讓 `docs/design/design-system.md` 成為 UX/開發的硬約束，並在 S5 後加一道 **S5.5 視覺關**（截圖 → 對照設計系統批判 → 退回）。profile 管 gate 嚴格度，UX 強度管 UX 深度，兩者互不決定對方。

PM 在 S1 宣告「**階段計畫**」依 profile 定基準再微調（無可見面跳 UX+折一致性、碰敏感面拆獨立資安棒）。開發/驗證關/收尾/retro 永不跳過。

```
 ┌────────────────────── 一個 SPRINT（standard 示意）──────────────────────┐
 S1. PM 規劃 ──► S2. UX 設計 ─┐  (無可見面則跳過 S2，S4 折進 S3 自檢)
                              ├─► S4. 一致性 gate ── CHANGES_REQUIRED → 退回
   S3. 架構（設計+拆解 一棒）─┘        │                                (上限2輪)
                                       ▼ PASS
                            S5. 開發 ◄──────────────┐
                                       ▼            │
                    S5.5 視覺關（UX 強度=full）─────┤ CHANGES_REQUIRED
                     截圖→對照 design-system→批判   │ 退回 S5（窄context，上限2輪）
                                       ▼ PASS/SKIPPED
              S6. 驗證關（形態依 profile）──────────┤ 退回 S5（窄context，上限3輪）
                lean : reviewer(功能+資安+飄移)     │ 飄移→補ADR/記backlog
                std  : QA ─► reviewer(資安+飄移)    │
                max  : QA ─► security ─► drift ─────┘
                                       ▼ PASS
                            S7. PM 收尾（瘦身，只讀 VERDICT）
                                       ▼
                            S8. retro 回顧 ──► docs/LESSONS.md（自動累積）
                                       │         docs/retro/（改善提案，待核可）
                                       ▼
                              [HUMAN GATE] 摘要 + 待核可提案
 └────────────────────────────────────────────────────────────────────────┘
                                       ▼ 放行
                                下一個 sprint (N+1)
              ▲ LESSONS.md 被下個 sprint 所有角色開工時讀取（學習回路）
```

## 角色與產物

| 階段 | 角色 | 產物 | gate? | 跑在哪個 profile |
|------|------|------|-------|------|
| S1 | pm                   | `sprints/sprint-N.md`（目標、驗收標準、DoD、profile） | | 全部 |
| S2 | ux-designer          | `design/ux/sprint-N-ux.md` | | 有可見面才跑 |
| S3 | architect            | `design/tech/sprint-N-tech.md` + `sprints/sprint-N-tasks.md` + ADR（**一棒融合**） | | 全部 |
| S4 | consistency-reviewer | `design/review/sprint-N-consistency.md` | ✅ | standard(有可見面)/max；lean 折進 S3 |
| S5 | developer            | 程式碼 + `sprints/sprint-N-dev.md` | | 全部 |
| S5.5 | **visual-reviewer** | `sprints/sprint-N-visual.md` + `design/ux/screenshots/sprint-N/` | ✅ | UX 強度=`full` 且有可見面 |
| S6 | **reviewer**（合併）  | `sprints/sprint-N-review.md` | ✅ | lean（全包）/ standard（資安+飄移） |
| S6 | qa / security / drift-auditor | `-qa.md` / `-security.md` / `-drift.md` | ✅ | standard(QA)／max(全拆)／PM 標拆資安 |
| S7 | pm                   | 更新 backlog + sprint log 摘要（瘦身，不重驗 AC） | | 全部 |
| S8 | retro                | `docs/LESSONS.md`(自動) + `docs/retro/sprint-N-retro.md`(提案) | 🧑 human | 全部 |

## 設計理念
- **驗收標準是客觀標尺**：PM 在 S1 就把需求寫成可測條件，驗證關（功能/飄移）才有依據，不靠感覺。
- **安全左移**：威脅模型在架構設計(S3)就種下，驗證關的資安區塊只是驗證覆蓋，不是末端補救。
- **ADR 帳本**：架構決策被記錄，驗證關的飄移區塊能機械式對照，而非事後驚覺長歪。
- **可追溯**：backlog id → sprint 項目 → 任務 → 驗收標準，一條線串到底。
- **檔案即交接**：subagent 不共享記憶，`docs/` 是它們唯一的「會議記錄」。
- **成本隨風險伸縮（profile）**：lean/standard/max 讓小專案不必付全套儀式——合併 gate、融合架構棒、瘦身收尾都是為了砍掉「重複做同樣的事」與冷啟動重讀。安全護欄（TDD、資安 High 不放行、退回上限、報告落檔、retro 提案需核可）在每個 profile 都保留。
- **自我學習，分風險**：retro(S8) 把可累積的教訓自動寫進 `LESSONS.md`（安全，全體下輪讀取）；改寫角色指令/流程則只「提案」到 `docs/retro/`，人類核可後才套用——避免機制自我退化或刪掉護欄。FRAMEWORK 級改善核可後回流到 dev-factory 源頭。
- **品味 = 約束 + 回饋，不是 prompt**：沒有設計師時，`design-system.md` 就是設計師——它是 UI 工作的**輸入約束**（ux-designer 只能用既有 token、developer 照 token 實作），不是事後檢查表。而 S5.5 視覺關是整條管線裡**唯一真的看過成品**的一棒：其他角色都只讀得到文字，只有它能發現「規格說適當間距、實際擠成一團」。兩者缺一不可——研究顯示有視覺 critic 的迭代帶來 +17.8% 品質，沒 critic 的純重新生成只有 +1.5%。
- **治理在外、執行在內（與 superpowers 並存）**：dev-factory 自己是治理/編排層（sprint 劇本、gate、可追溯、自我學習）；各棒「內部怎麼做」則委派給 [superpowers](https://github.com/obra/superpowers) 的成熟紀律——developer 走 `test-driven-development`、architect 拆解用 `writing-plans`、qa/reviewer 用 `systematic-debugging`、explorer 用 `brainstorming`。orchestrator 永遠是唯一外層，superpowers 不接管派工/收尾。superpowers 為選用依賴（建議使用者層安裝），未裝時各 agent 有內嵌後備規則。

## 護欄
- 每個修復迴圈有上限（一致性 2 輪、驗證關退回 3 輪）；各 gate 計數**獨立且不重置**，另有 **sprint 總修復預算 6 次**（任何 gate 的退回都累計）——達上限或預算即升級給使用者，防 gate 之間互彈空轉。
- **狀態落地**：階段進度與所有迴圈計數記在 sprint 主檔的「執行狀態」區塊（orchestrator 每階段更新）；context 壓縮或中斷後以它為準續跑，不憑記憶。gate 報告第一行固定 `VERDICT: <判定>`，orchestrator 只讀判定與問題清單，控制 context 成本。
- **分支隔離**：每個 sprint 在 `sprint-<N>` 分支上進行；合併回主分支由收尾 human gate 決定，orchestrator 不自行 merge。
- 預設每個 sprint 收尾停下等放行；要連跑用 `/loop /sprint`。
- 全自動連跑前，務必先跑通單輪，確認交接檔案真的有被讀寫。
