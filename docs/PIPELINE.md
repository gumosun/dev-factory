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

完整一輪 sprint 的 10 個階段。每關是 **agent gate**（不過退回上一棒重跑，不打擾使用者），只有階段 10 收尾是 **human gate**。

```
 ┌─────────────────────────── 一個 SPRINT ───────────────────────────┐
 1. PM 規劃 ──► 2. UX 設計 ─┐
                            ├─► 4. 一致性交叉檢查 (gate)
              3. 技術設計 ──┘        │ CHANGES_REQUIRED → 退回 2/3
                                     ▼ PASS
                            5. 任務拆解 + 測試/安全需求
                                     ▼
                            6. 開發 ◄──────────────┐
                                     ▼             │ FAIL/FINDINGS
                            7. QA (gate) ──────────┤ 退回 6（上限3輪）
                                     ▼ PASS        │
                            8. 資安驗證 (gate) ────┤
                                     ▼ PASS        │
                            9. 飄移稽核 (gate) ────┘ DRIFT→退回/補ADR/記backlog
                                     ▼ ALIGNED
                            10. PM 收尾
                                     ▼
                            11. retro 回顧 ──► docs/LESSONS.md（自動累積）
                                     │         docs/retro/（改善提案，待核可）
                                     ▼
                              [HUMAN GATE] 摘要 + 待核可提案
 └────────────────────────────────────────────────────────────────────┘
                                     ▼ 放行
                              下一個 sprint (N+1)
              ▲ LESSONS.md 被下個 sprint 所有角色開工時讀取（學習回路）
```

## 角色與產物

| 階段 | 角色 | 產物 | gate? |
|------|------|------|-------|
| 1  | pm                   | `sprints/sprint-N.md`（目標、驗收標準、DoD） | |
| 2  | ux-designer          | `design/ux/sprint-N-ux.md` | |
| 3  | architect            | `design/tech/sprint-N-tech.md` + ADR | |
| 4  | consistency-reviewer | `design/review/sprint-N-consistency.md` | ✅ |
| 5  | architect            | `sprints/sprint-N-tasks.md` | |
| 6  | developer            | 程式碼 + `sprints/sprint-N-dev.md` | |
| 7  | qa                   | `sprints/sprint-N-qa.md` | ✅ |
| 8  | security             | `sprints/sprint-N-security.md` | ✅ |
| 9  | drift-auditor        | `sprints/sprint-N-drift.md` | ✅ |
| 10 | pm                   | 更新 backlog + sprint log 摘要 | |
| 11 | retro                | `docs/LESSONS.md`(自動) + `docs/retro/sprint-N-retro.md`(提案) | 🧑 human |

## 設計理念
- **驗收標準是客觀標尺**：PM 在階段1就把需求寫成可測條件，QA(7) 與飄移(9) 才有依據，不靠感覺。
- **安全左移**：威脅模型在技術設計(3)就種下，資安(8)只是驗證覆蓋，不是末端補救。
- **ADR 帳本**：架構決策被記錄，飄移稽核(9)能機械式對照，而非事後驚覺長歪。
- **可追溯**：backlog id → sprint 項目 → 任務 → 驗收標準，一條線串到底。
- **檔案即交接**：subagent 不共享記憶，`docs/` 是它們唯一的「會議記錄」。
- **自我學習，分風險**：retro(11) 把可累積的教訓自動寫進 `LESSONS.md`（安全，全體下輪讀取）；改寫角色指令/流程則只「提案」到 `docs/retro/`，人類核可後才套用——避免機制自我退化或刪掉護欄。FRAMEWORK 級改善核可後回流到 dev-factory 源頭。
- **治理在外、執行在內（與 superpowers 並存）**：dev-factory 自己是治理/編排層（sprint 劇本、gate、可追溯、自我學習）；各棒「內部怎麼做」則委派給 [superpowers](https://github.com/obra/superpowers) 的成熟紀律——developer 走 `test-driven-development`、architect 拆解用 `writing-plans`、qa/developer 用 `systematic-debugging`、explorer 用 `brainstorming`。orchestrator 永遠是唯一外層，superpowers 不接管派工/收尾。superpowers 為選用依賴（建議使用者層安裝），未裝時各 agent 有內嵌後備規則。

## 護欄
- 每個修復迴圈有上限（一致性 2 輪、QA/資安各 3 輪）；達上限升級給使用者。
- 預設每個 sprint 收尾停下等放行；要連跑用 `/loop /sprint`。
- 全自動連跑前，務必先跑通單輪，確認交接檔案真的有被讀寫。
