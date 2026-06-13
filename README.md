# dev-factory

一套**可複用**的多角色自主開發機制，跑在 Claude Code 上。給它一個專案目標與 backlog，它會以 orchestrator 主持 PM → UX → 技術設計 → 一致性檢查 → 開發 → QA → 資安 → 飄移稽核 → 收尾的完整 sprint，角色之間透過檔案交接，gate 不過自動退回重跑，只在 sprint 收尾或卡關時找你。

這個資料夾是「真相來源」，用 `install.sh` 裝進任何專案。

## 內容
```
dev-factory/
├── agents/        9 個角色 subagent 定義（含 retro 自我學習）
├── skills/sprint/ orchestrator（/sprint 劇本）
├── templates/     CLAUDE.md 契約 + PROJECT_GOAL/backlog/LESSONS/ADR/sprint 範本
├── docs/PIPELINE.md  完整流程圖與設計理念
└── install.sh     裝進目標專案
```

## 快速開始
```bash
# 1. 在「新專案」根目錄安裝
cd /path/to/your-new-project
~/Desktop/dev-factory/install.sh

# 2. 填目標與待辦
#    編輯 docs/PROJECT_GOAL.md、docs/backlog.md

# 3. 在該專案開 Claude Code
#    Shift+Tab 切到 accept-edits 權限模式（讓它連續動手不每步問你）

# 4. 開場輸入：
#    讀 CLAUDE.md，依自主 sprint 工作流開始開發，先跑單輪後給我摘要
```

確認單輪跑通、`docs/` 交接檔案有正常產出後，再用 `/loop /sprint` 連跑多個 sprint。

## 安裝模式
- **專案層級（預設）**：複製進 `<project>/.claude/`，專案自我完備、可進 git。升級框架就重跑 install。
- **使用者層級**：`install.sh --user` 裝到 `~/.claude/`，所有專案共用 agents 與 `/sprint`（每個專案仍需各自的 CLAUDE.md + docs/）。

## 運作原理（重點）
- Claude Code 的 subagent **不會自發互相討論**；是 orchestrator（主 session）把上一棒的產出餵給下一棒，編排成回合制流程。
- subagent **不共享記憶**，唯一交接方式是 `docs/` 檔案，所以每個角色都被要求「開頭先讀、結尾必寫」。
- gate（一致性/QA/資安/飄移）不過會**自動退回**對應角色，有迴圈上限，達上限才升級給你。
- **自我學習**：每個 sprint 後 retro 回顧摩擦點 → 教訓自動累積進 `docs/LESSONS.md`（全體下輪會讀）；改寫角色指令/流程則只提案到 `docs/retro/`，由你核可後才套用（FRAMEWORK 級的回流到本框架源頭）。記憶自動長、流程改靠 gate。

詳見 `docs/PIPELINE.md`。

## 客製
- 不需要某個角色（例如純後端不用 UX）→ 刪掉對應 `agents/*.md`，並在 `skills/sprint/SKILL.md` 拿掉該步。
- 想換各角色的模型（成本/品質）→ 改 agent frontmatter 的 `model:`。
- 想調「多自主 / 多停下問你」→ 改 `templates/CLAUDE.md` 的「自主邊界」段。
```
