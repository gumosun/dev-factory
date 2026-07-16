# dev-factory

一套**可複用**的多角色自主開發機制，跑在 Claude Code 上。兩段式：

- **`/discovery`（前置，選用）**：只有方向、還沒具體構想時，agent 幫你發散概念、用證據反覆批判驗證、收斂成專案目標。
- **`/sprint`（建造）**：給定目標與 backlog，orchestrator 主持 PM → UX → 架構（設計+拆解一棒）→ 一致性 → 開發 → 視覺關 → 驗證關 → 收尾的 sprint，角色之間透過檔案交接，gate 不過自動退回重跑，只在 sprint 收尾或卡關時找你。**流程隨「治理 profile」（lean/standard/max）伸縮**——這是控制時間與 token 成本的主鈕：lean 把驗證關合併成單一 reviewer、一致性折進架構自檢；max 全拆專家棒。

已經很確定要做什麼？直接填目標跑 `/sprint`，跳過 discovery。各棒「內部怎麼做」委派給 [superpowers](https://github.com/obra/superpowers) 的成熟紀律（TDD、writing-plans、systematic-debugging、brainstorming…），dev-factory 自己專注在治理/編排。

這個資料夾是「真相來源」，用 `install.sh` 裝進任何專案。

## 內容
```
dev-factory/
├── agents/          14 個角色 subagent（建造11：含合併驗證關 reviewer + 視覺關 visual-reviewer + discovery 3: explorer/critic/shaper）
├── skills/sprint/   建造 orchestrator（/sprint 劇本）
├── skills/discovery/ 前置 orchestrator（/discovery 劇本）
├── templates/       CLAUDE.md 契約 + PROJECT_GOAL/backlog/DIRECTION/LESSONS/rubric/ADR/sprint/design-system 範本
├── docs/PIPELINE.md 完整流程圖與設計理念
└── install.sh       裝進目標專案
```

## 前置依賴：superpowers（建議）
各 agent 的執行紀律會優先呼叫 superpowers skill（未安裝則走內嵌後備）。建議使用者層安裝一次，所有專案共用：
```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

## 快速開始
```bash
# 1. 在「新專案」根目錄安裝
cd /path/to/your-new-project
~/Desktop/dev-factory/install.sh

# 2a. 已經知道要做什麼 → 填目標與待辦
#     編輯 docs/PROJECT_GOAL.md、docs/backlog.md，跑 /sprint
# 2b. 只有方向、還沒構想 → 填方向
#     編輯 docs/DIRECTION.md（可調 docs/discovery/rubric.md 權重），先跑 /discovery
#     收斂出 PROJECT_GOAL+backlog 後再進 /sprint

# 3. 在該專案開 Claude Code
#    Shift+Tab 切到 accept-edits 權限模式（讓它連續動手不每步問你）

# 4. 開場輸入（建造）：
#    讀 CLAUDE.md，依自主 sprint 工作流開始開發，先跑單輪後給我摘要
#    或（前置）：讀 CLAUDE.md，我只有方向還沒構想，跑 /discovery 幫我收斂
```

確認單輪跑通、`docs/` 交接檔案有正常產出後，再用 `/loop /sprint` 連跑多個 sprint。

## 安裝模式
- **專案層級（預設）**：複製進 `<project>/.claude/`，專案自我完備、可進 git。升級框架就重跑 install；並播種 `.claude/settings.json` 權限 allowlist（WebSearch/WebFetch，建議自行補上測試指令），減少自主連跑時的權限提示。
- **使用者層級**：`install.sh --user` 裝到 `~/.claude/`，所有專案共用 agents 與 `/sprint`；每個專案再跑 `install.sh --seed-only <path>` 鋪 CLAUDE.md + docs/。
- **升級保護**：install 會記錄檔案 hash（`.dev-factory-manifest`）。重跑時凡你本地改過的 agents/skills（例如已核可的 PROJECT-local 客製）一律跳過並警告，確定要覆蓋加 `--force`。

## 運作原理（重點）
- Claude Code 的 subagent **不會自發互相討論**；是 orchestrator（主 session）把上一棒的產出餵給下一棒，編排成回合制流程。
- subagent **不共享記憶**，唯一交接方式是 `docs/` 檔案，所以每個角色都被要求「開頭先讀、結尾必寫」。
- gate（一致性 / 驗證關）不過會**自動退回**對應角色，退回時給 developer 窄 context（只碰被點名的檔）省 token；有迴圈上限與 sprint 總修復預算，達上限才升級給你。
- **治理 profile（省時省 token 主鈕）**：`/sprint` 首次開跑會依專案規模建議 lean / standard / max 讓你選一次（寫進 `PROJECT_GOAL.md`）。lean 只跑約 5 棒（單一合併 reviewer），standard 是預設全流程，max 全拆專家棒。profile 只改「跑幾棒」，不改模型；安全護欄每個 profile 都保留。
- **UX 強度（UI 品質主鈕，正交於 profile）**：`light`（預設）＝現行行為；`full` 讓 `docs/design/design-system.md`（鋪進來的 Stripe 風預設，可整份換）成為 UX/開發的**硬約束**，並加一道 **S5.5 視覺關**——visual-reviewer 起專案截圖、讀圖、對照設計系統批判、不過退回。**沒有設計師也能有品味**靠的是這個：品味 = 約束 + 回饋，不是把「請做得好看」寫進 prompt。
- **狀態落地**：sprint 進度、gate 退回計數記在 sprint 主檔的「執行狀態」區塊，中斷或 context 壓縮後可續跑；每個 sprint 在 `sprint-<N>` 分支上進行，合併由你在收尾 gate 決定。PM 會在 S1 宣告「階段計畫」，無使用者可見面自動跳過 UX+一致性、無新攻擊面資安合併快掃，流程隨工作量伸縮。
- **自我學習**：每個 sprint 後 retro 回顧摩擦點 → 教訓自動累積進 `docs/LESSONS.md`（全體下輪會讀）；改寫角色指令/流程則只提案到 `docs/retro/`，由你核可後才套用（FRAMEWORK 級的回流到本框架源頭）。記憶自動長、流程改靠 gate。

詳見 `docs/PIPELINE.md`。

## 客製
- **想省時間/token → 先調治理 profile**（`docs/PROJECT_GOAL.md` 的「治理 profile」欄位）：lean 最省、standard 平衡、max 最嚴。這是成本主鈕，優先動它，不用改任何 agent。
- **不喜歡預設的視覺風格** → 整份換掉 `docs/design/design-system.md`。預設是 Stripe 風（暖中性色、慷慨留白、分層陰影、彩度主色），適合面向使用者的產品；資料密集的後台換成更緊的 Linear/Vercel 風更合適。換時保持 `## Design Tokens` / `## 元件` / `## 禁用規則` 三個 section 標題不變（agent 靠它們定位）。install 重跑**不會**覆蓋你改過的設計系統。
- 不需要某個角色（例如純後端不用 UX）→ 刪掉對應 `agents/*.md`，並在 `skills/sprint/SKILL.md` 拿掉該步。
- 想換各角色的模型（成本/品質）→ 改 agent frontmatter 的 `model:`。
- 想調「多自主 / 多停下問你」→ 改 `templates/CLAUDE.md` 的「自主邊界」段。
```
