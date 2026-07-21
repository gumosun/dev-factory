# dev-factory

**跑在 Claude Code 上的可複用多角色自主開發框架**——把一整個軟體團隊（PM → UX → 架構 → 開發 → QA → 資安）編排成自主 agent，配上品質 gate、檔案交接、以及會自我學習的 retro 迴圈。

已在真實專案上實戰 **30+ 個自主 sprint**，每次 retro 的教訓都回流進框架本身。

[English README](README.md)

---

## 為什麼需要它

Coding agent 很會「寫程式」，但很不會「當一個團隊」：跳過設計、偏離架構、從不記取教訓。dev-factory 補上缺失的治理層：

- **角色分工**——14 個專職 subagent，每個只做一件事、必留書面產出
- **品質 gate**——一致性 / 視覺 / QA / 資安 / 飄移各關，不過**自動退回重做**，有迴圈上限防止空轉
- **檔案交接**——subagent 不共享記憶，`docs/` 是唯一真相來源；backlog → sprint → 任務 → 驗收標準一條線可追溯
- **自我學習**——每個 sprint 結尾 retro，教訓自動累積進 `LESSONS.md`（下輪全體必讀）；改流程/角色指令則需人類核可——框架會進步，但不會自己拆掉護欄

## Gate 退回實際長什麼樣

真實、未經編輯的交接檔案，來自 31 個 sprint 實戰的第 31 輪——PM 規格把設計系統宣告為硬約束，視覺關對真實服務截圖批判、把一個阻擋項帶著窄 context 退回 developer、複驗放行；retro 的教訓餵給下一輪所有角色：

![真實交接檔案：規格 → 視覺關退回 → 機構記憶](docs/assets/handoff-artifacts.png)

## 兩段式管線

- **`/discovery`（前置，選用）**：只有方向、還沒具體構想時，agent 發散 3–5 個概念、依 rubric（有人要嗎/做得出來嗎/值得做嗎/能便宜驗證嗎）用證據反覆批判、收斂成你核可的專案目標。**禁止憑感覺**。
- **`/sprint`（建造）**：orchestrator 主持 S1 PM 規劃 → S2 UX → S3 架構 → S4 一致性關 → S5 開發（TDD）→ S5.5 視覺關 → S6 驗證關（QA/資安/飄移）→ S7 收尾 → S8 retro。gate 不過自動退回，退回時給窄 context（只碰被點名的檔）省 token；只在 sprint 收尾或達迴圈上限時找你。

完整流程圖見 [docs/PIPELINE.md](docs/PIPELINE.md)。

## 成本隨風險伸縮

兩顆正交的主鈕，每專案問一次：

| 主鈕 | 選項 | 控制什麼 |
|------|------|----------|
| **治理 profile** | `lean` / `standard` / `max` | 跑幾道 gate——lean 把驗證關合併成單一 reviewer（約 5 棒），max 全拆專家棒。安全護欄（TDD、資安 High 不放行、退回上限）每個 profile 都保留。 |
| **UX 強度** | `light` / `full` | `full` 讓 `design-system.md` 成為**硬約束**（agent 只能用既有 token），並加 S5.5 視覺關——整條管線唯一真的「看過成品」的一棒。品味 = 約束 + 回饋，不是把「請做得好看」寫進 prompt。 |

## 成本觀測層：token-lens（可選、預設不花額外 token）

大家都在用 AI，但幾乎沒人在管 token 的 ROI。dev-factory 內建一套**可選**的觀測與治理層 `token-lens`，掛在流程外側——**觀測層與執行層分離、變更走人類核可**，非 AI 專案零額外開銷：

| 模組 | 掛載點 | 做什麼 | 花不花 token |
|------|--------|--------|--------------|
| **Ledger** | retro（條件式） | 解析 session 紀錄，把成本＋品質訊號（工具錯誤率）歸戶到專案／模型／agent 角色 | 解析零 token；只有成本或錯誤率**超過門檻**才動用 agent 判讀、把優化教訓寫進 LESSONS |
| **Router** | architect（條件式） | 產品功能會呼叫 LLM／multi-agent 時，指揮家在技術設計階段依判斷密度指派模型層級，寫進 ADR 的「LLM 成本設計」節 | 純非 AI 專案整段跳過；有 LLM 用途才花 |
| **Radar** | Router 呼叫 | 抓官方模型／定價文件＋跨模型情報（價／品質／速度），diff 出新模型與價格變動，供 Router 用當前合法 model id 與冷啟動先驗 | curl 腳本，零 token |
| **retro_optimize**（學習引擎） | retro（條件式） | 把每輪成本×品質 → champion／challenger 晉升提案（帕累托規則＋criticality 硬地板）；**晉升走人類核可，引擎不自改建議表** | 解析零 token；判讀才花 |

**設計原則**：① 量測免費、判讀才花錢——解析是純 Python，只有數字超門檻才動 agent；② 降層主張必須附品質代理證據（gate 通過率／退回迴圈／工具錯誤率），**降層不降質才算省**；③ 改角色 model 指派走人類核可，與 retro 的護欄同一條線——AI 的自主性要有邊界，連成本工具自己都遵守。門檻可調（`.claude/token-lens/thresholds.txt`）。

**自我學習迴圈**：Radar 情報（唯讀）→ 建議表（決策的 SoR）→ Router 依「任務 × criticality」派工 → sprint 執行 → retro 評估（三向觸發：品質↑升級／成本↑降級／Radar 機會）→ 帕累托＋硬地板 → **人類 Gate** ↺ 寫回建議表。結構上就是廣告平台優化素材／出價用的 champion／challenger＋canary＋holdout 迴圈，被優化對象換成「模型選擇」。

> `token-lens` 同時是一個**可獨立展示的 repo**——完整專案（含 22 個單元測試與視覺報告 `report.html`）在其自有 repo，此處 `vendor/token-lens/` 是被鋪進專案的 runtime 快照（見 `vendor/token-lens/UPSTREAM.md`，用 `sync-from-upstream.sh` 同步）。

## 快速開始

```bash
# 1. 在專案根目錄安裝
cd /path/to/your-project
/path/to/dev-factory/install.sh

# 2a. 已經知道要做什麼 → 填 docs/PROJECT_GOAL.md + docs/backlog.md，跑 /sprint
# 2b. 只有方向 → 填 docs/DIRECTION.md，先跑 /discovery

# 3. 在該專案開 Claude Code
#    Shift+Tab 切到 accept-edits 權限模式（讓它連續動手不每步問你）

# 4. 開場輸入：
#    讀 CLAUDE.md，依自主 sprint 工作流開始開發，先跑單輪後給我摘要
```

確認單輪跑通、`docs/` 交接檔案有正常產出後，再用 `/loop /sprint` 連跑多個 sprint。

### 前置依賴（建議）：superpowers

各角色「內部怎麼做」（TDD、systematic-debugging、writing-plans…）委派給開源的 [superpowers](https://github.com/obra/superpowers) plugin，dev-factory 自己專注在治理/編排。建議使用者層安裝一次：

```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

未安裝時各 agent 走內嵌後備規則。

## 安裝模式

- **專案層級（預設）**：複製進 `<project>/.claude/`，專案自我完備、可進 git。升級框架就重跑 install。
- **使用者層級**：`install.sh --user` 裝到 `~/.claude/` 所有專案共用；每個專案再跑 `install.sh --seed-only <path>` 鋪種子檔。
- **升級保護**：install 記錄檔案 hash（`.dev-factory-manifest`），重跑時凡你本地改過的一律跳過並警告，確定要覆蓋加 `--force`。

## 內容

```
dev-factory/
├── agents/           14 個角色 subagent（建造 11 + discovery 3：explorer/critic/shaper）
├── skills/sprint/    建造 orchestrator（/sprint 劇本）
├── skills/discovery/ 前置 orchestrator（/discovery 劇本）
├── templates/        CLAUDE.md 契約 + 目標/backlog/教訓/ADR/設計系統範本
├── vendor/ui-ux-pro-max/  vendored 設計資料庫 + 生成腳本（MIT；鋪到專案 .claude/uipro/，S0 量身 preset 用）
├── vendor/token-lens/     可選成本觀測＋自我學習路由層（ledger/quality/radar/router/retro_optimize + 政策/情報；鋪到專案 .claude/token-lens/。runtime 快照，上游為獨立 repo）
├── docs/PIPELINE.md  完整流程圖與設計理念
└── install.sh        安裝器
```

## 設計理念

- **驗收標準是客觀標尺**：PM 在 S1 就把需求寫成可測條件，驗證關才有依據，不靠感覺。
- **安全左移**：威脅模型在架構設計（S3）就種下，資安關只是驗證覆蓋，不是末端補救。
- **ADR 帳本**：架構決策被記錄，飄移關能機械式對照，而非事後驚覺長歪。
- **檔案即會議記錄**：subagent 不共享記憶，每次交接都是檔案，每個決策都可稽核。
- **自我學習，分風險**：教訓自動累積（安全）；改角色指令/流程只「提案」、需人類核可——避免機制自我退化或刪掉護欄。

完整理念與各階段對照表：[docs/PIPELINE.md](docs/PIPELINE.md)。

## 客製

- **想省時間/token** → 先調治理 profile（成本主鈕，不用改任何 agent）
- **不喜歡預設視覺風格** → 整份換掉 `docs/design/design-system.md`（預設 Stripe 風；保留 agent 定位用的三個 section 標題）
- **不需要某個角色** → 刪掉對應 `agents/*.md`，並在 `skills/sprint/SKILL.md` 拿掉該步
- **想換各角色的模型** → 改 agent frontmatter 的 `model:`
- **調「多自主 / 多停下問你」** → 改 `templates/CLAUDE.md` 的「自主邊界」段

### 既有專案升級到量身 preset

install.sh 不會覆蓋你專案裡的 `docs/design/design-system.md`。舊專案要吃到新東西有兩條路：

1. **只要 anti-slop 規則**：把 `templates/design-system.md` 禁用規則 11–14（emoji 圖示、hover 位移、AI 紫粉漸層、cursor: pointer）手動貼進你專案的 design-system.md。
2. **要量身 preset**：把你專案的 design-system.md 重置為出廠模板（含首行 `<!-- dev-factory-default-preset -->` marker），下次以 UX 強度=full 開跑時 S0 會依 PROJECT_GOAL 重新生成。

## 致謝

各角色的執行紀律委派給 [superpowers](https://github.com/obra/superpowers)（@obra，MIT）——它是**選用、另行安裝的外部依賴**，本 repo 不內含任何 superpowers 程式碼。dev-factory 本身是其上的治理/編排層。

S0 量身 preset 的設計資料庫與生成腳本來自 [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)（MIT）——這部分**以 MIT 授權 vendor 在 `vendor/ui-ux-pro-max/`**（含 LICENSE 與來源/版本註記，見該目錄 README）。

## License

[MIT](LICENSE)
