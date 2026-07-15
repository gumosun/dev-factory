# LESSONS — 累積教訓（機構記憶）

> 這份是整套機制的「自我學習」記憶體。retro 在每個 sprint 後**只附加**教訓進來。
> **讀取規則**：各角色開工前讀「通用」各區＋「各角色」底下**自己的小節**（不必整份讀，控制 context 成本）。
> **寫入規則**：只附加、不刪改既有條目（整併需走 retro 第2層提案、人類核可）。每條標日期與來源 sprint。
> 通用教訓進通用區；只跟某角色有關的，寫進該角色小節——放錯區＝沒人讀到。

## 通用：專案慣例 / 約定
<例：2026-06-13 (sprint-1) 所有時間一律存 UTC，前端才轉時區。>

## 通用：反覆出現的雷 / bug 模式
<例：2026-06-13 (sprint-1) 動到 schema 一定要同步更新 migration 與 seed，否則 QA 回歸會掛。>

## 通用：已驗證有效的做法
<例：2026-06-13 (sprint-1) 技術設計先畫資料流再定 schema，一致性 gate 一次就過。>
- 2026-06-24 (framework) 分層鐵則：dev-factory 治理層（sprint 劇本 / 4 gate / AC 可追溯 / ADR / LESSONS）是唯一外層；superpowers 只當各棒內部執行紀律，絕不讓 `using-superpowers / executing-plans / finishing-a-development-branch / using-git-worktrees` 接管派工、worktree 或收尾。

## 各角色

### pm

### ux-designer

### architect
- 2026-06-24 (framework) 架構棒 Part 2 任務拆解採 `superpowers:writing-plans` 格式（原子步驟 / Files / Interfaces / 禁 placeholder / 自檢），但**覆寫上游兩點**：輸出仍走 `docs/sprints/sprint-<N>-tasks.md`、不觸發其 execution-handoff/worktree（派工由 orchestrator 主導）。已實證 architect→developer→qa 全鏈能用此格式串接（檔案即交接、AC 可追溯不受干擾）。

### consistency-reviewer

### developer
- 2026-06-24 (framework) 走強制 TDD（`superpowers:test-driven-development`）：先寫失敗測試、親眼看到紅燈才實作，一任務一 commit。已實證可運作（git 歷史顯示實作只出現在綠燈 commit）。
- 2026-06-24 (framework) 被 QA/security 退回時，先用 `superpowers:receiving-code-review` 技術驗證回饋是否成立（不盲從），再用 `superpowers:systematic-debugging` 找根因、寫重現測試，才循 TDD 修——修症狀不算修好。

### qa
- 2026-06-24 (framework) 開 issue 前用 `superpowers:systematic-debugging` 查根因，issue 要帶根因/可疑層而非只報症狀（只在發現失敗時觸發）。

### reviewer（合併驗證關；lean/standard 用）

### security

### drift-auditor

### retro

### explorer / critic / shaper（discovery）
