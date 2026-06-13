# dev-factory 開發流程（PIPELINE）

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

## 護欄
- 每個修復迴圈有上限（一致性 2 輪、QA/資安各 3 輪）；達上限升級給使用者。
- 預設每個 sprint 收尾停下等放行；要連跑用 `/loop /sprint`。
- 全自動連跑前，務必先跑通單輪，確認交接檔案真的有被讀寫。
