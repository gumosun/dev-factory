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

## License

[MIT](LICENSE)
