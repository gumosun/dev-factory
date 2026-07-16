# UX Track C + B 設計規格

日期：2026-07-16
狀態：待實作

## 問題

dev-factory 的 UX 能力太弱。`ux-designer` 只產出 markdown 規格，沒有任何設計品味的來源，也沒有任何人看過成品長什麼樣——整條管線從頭到尾沒有一隻眼睛。結果是可出貨的 UI 品質不足。

使用者是 solo 開發者，**沒有設計師**，所以解法不能依賴人類設計師的產出（Figma 檔、設計稿）。

## 解法概述

依先前 deep-research 的結論（記錄在 memory `reference-ai-ui-taste-research`）：**品味 = 約束 + 回饋**，不是靠 prompt 講「請做得好看」。因此實作兩塊：

- **Track C — 設計系統約束層**：一份具體的設計系統檔進到專案，當作 UI 工作的**輸入約束**（不是檢查表）。這是「設計師的替代品」。
- **Track B — 視覺回饋關**：新 `visual-reviewer` 一棒，渲染 → 截圖 → 對照設計系統批判 → 退回修。這是研究中實測的**因果品質驅動力**（有 critic +17.8%／無 critic 僅 +1.5%）。

兩者由一個正交於 governance profile 的 **`UX 強度`** 開關控制。

## 設計決策（已定案）

| 決策 | 選擇 | 理由 |
|---|---|---|
| Track C 形態 | 內建靜態設計系統檔 | dev-factory 會被 install 進**別的專案**；每多一個 MCP 依賴＝每個目標專案都要各裝一次。靜態檔零依賴、符合現有「檔案即交接」哲學。代價：不會自動跟上游更新（可接受，整份可換）。 |
| 預設 preset 品味 | **Stripe 風** | Linear/Vercel 那派是為開發者工具長的（高對比單色、緊密、扁平、1px 邊框），套到一般產品太冷、工具感太強。Stripe 風暖中性色、慷慨留白、分層陰影、有彩度主色，產品感與親和力強。取捨：資料密集後台會顯得鬆——真遇到再換 preset。 |
| Track B 截圖方式 | Bash + playwright CLI | 不強迫目標專案裝 MCP，只需專案有 node。 |
| UX 開關 | 獨立 `UX 強度：light / full`，正交於 profile | UX 需求與風險等級是兩件事：內部工具可能 lean 但要好看；後端服務可能 max 但沒 UI。 |
| visual gate 位置 | S5 後獨立迴圈（S5.5） | 視覺 critique 需要看圖迭代，節奏與功能驗證不同，混在一起兩邊都做不深。折進 S6 會稀釋；讓 developer 自我批判則放棄 Track B 的主要效益。 |
| 預設值 | `light`（＝現狀） | 不動既有專案；要吃這套在 PROJECT_GOAL 標 `full`。 |

## 架構

### 1. `docs/design/design-system.md`（Track C）

由 `templates/design-system.md` 在 install 時鋪進專案。**具體到可照抄**，不是抽象原則：

- **Design tokens**：色彩（主色/中性/語意色，含實際色值）、間距 scale、字級 scale、圓角、陰影層級
- **元件清單**：按鈕/輸入/卡片/表格/對話框等的用法與變體
- **禁用規則**：不得自創 scale 外的色值/間距；不得用邊框取代既定的陰影分隔；等
- **檔頭聲明**：這是預設品味，整份可換掉

**三棒共讀，且有人查**——這是把「建議」變成「約束」的關鍵：

| 角色 | 怎麼用 |
|---|---|
| `ux-designer` | 寫規格時只能引用檔內既有 token/元件；要新東西標 `⚠️ 需擴充 design system` |
| `developer` | 實作照 token 寫，不自創色值 |
| `visual-reviewer` | 拿它當檢查表批判截圖 ← **執行點** |

### 2. `agents/visual-reviewer.md`（Track B）

- **tools**：`Read, Write, Edit, Bash, Glob`
- **model**：需要視覺判斷力 → `opus`（與 developer 同級；critique 品質是這一棒的全部價值）

流程：

1. Bash 起 dev server（指令來自 PROJECT_GOAL 的「預覽指令」欄）
2. `npx playwright screenshot` 對各畫面 × 斷點 × 狀態產圖 → `docs/design/ux/screenshots/sprint-<N>/`
3. Read 讀圖
4. 對照 `docs/design/design-system.md` + `docs/design/ux/sprint-<N>-ux.md` 批判：版面、資訊層級、對比、RWD、a11y、token 遵循
5. Write 產 `docs/sprints/sprint-<N>-visual.md`，第一行固定 `VERDICT:`

**VERDICT 三態**：
- `PASS` → 進 S6
- `CHANGES_REQUIRED` → 窄 context 退回 developer
- `SKIPPED` → 起不來/無法渲染。**必須寫明理由**，不准靜默跳過，但不擋 sprint

沿用 R-15-1 落檔鐵則。

### 3. `UX 強度` 開關

`docs/PROJECT_GOAL.md` 新欄位，與 `治理 profile` 並列：

- **`light`**（預設）：現狀。ux-designer 僅在有可見面時跑，無設計系統約束、無視覺關。
- **`full`**：三棒共讀 design-system + 啟用 S5.5 視覺關。

與 profile 交互：**互不干涉**（profile 管 gate 嚴格度，UX 強度管 UX 深度）。

與「本輪無使用者可見面」交互：即使 `full`，無可見面 → 跳過 S2 與 S5.5（PM 在階段計畫宣告，與現有邏輯一致）。

首次開跑時 `/sprint` 與 profile **同一次**問（每專案一次），寫回 PROJECT_GOAL。

### 4. S5.5 視覺迴圈

```
S5. 開發 ──► S5.5 視覺關 ──PASS/SKIPPED──► S6. 驗證關
      ▲          │ CHANGES_REQUIRED
      └──────────┘ 窄 context 退回（上限 2 輪，計入總修復預算 6）
```

護欄全部沿用現有機制：
- 退回上限 **2 輪**，計數**獨立且不重置**
- 計入 **sprint 總修復預算 6 次**
- 計數記在 sprint 主檔「執行狀態」區塊（斷點續跑真理來源）
- 達上限仍不過 → 升級使用者
- 退回時附「本輪只需碰：<點名檔案>」（窄 context 鐵則）

### 5. 預覽指令

`docs/PROJECT_GOAL.md` 的「技術約束 / 偏好」區新增一欄：**預覽指令**（例：`npm run dev`，port 3000）。visual-reviewer 靠它起專案。缺這欄 → visual-reviewer 回 `SKIPPED` 並說明。

## 檔案變更清單

**新增（2）**
- `templates/design-system.md` — Stripe 風 token set + 元件 + 禁用規則
- `agents/visual-reviewer.md` — Track B 的一棒

**修改（9）**
- `agents/ux-designer.md` — full 時讀 design-system、只引用既有 token、`⚠️ 需擴充 design system` 標記
- `agents/developer.md` — 有 UI 且 full 時照 token 實作；新增「被 S5.5 退回」的處置（與現有「被驗證關退回」同構）
- `skills/sprint/SKILL.md` — UX 強度判定（併入 profile 提問）、S5.5 劇本、迴圈計數、裁剪規則
- `templates/PROJECT_GOAL.md` — `UX 強度` 欄 + `預覽指令` 欄
- `templates/CLAUDE.md` — UX 強度說明、自主邊界 (f) 併入 UX 強度提問
- `templates/sprint-log-template.md` — 執行狀態區塊加 S5.5 階段與計數欄
- `docs/PIPELINE.md` — 流程圖 + 角色表 + 設計理念補述
- `install.sh` — 鋪 `design-system.md`、建 screenshots 目錄、更新角色數提示
- `README.md` — 角色清單與 UX 強度說明

## 不做（YAGNI）

- **Track A（Figma 匯入）**：無設計師、無 Figma 檔。
- **Lovable 整合**：無 API/CLI，無法自動化；只能當人工前置步驟。
- **Better Design / shadcn MCP**：見上方決策表；靜態檔已足夠，MCP 是每專案的安裝負擔。
- **多 preset 切換機制**：先出一份 Stripe 風預設；要換就整份改檔。真的需要多份再說。
- **視覺回歸比對（跨 sprint 截圖 diff）**：不同問題，先不做。

## 驗證方式

1. `./install.sh --seed-only <tmpdir>` → 確認 `design-system.md` 與 screenshots 目錄鋪出來、PROJECT_GOAL 有兩個新欄位
2. 對既有 `light` 專案跑一輪 → 確認行為完全沒變（不回歸）
3. 開一個 `full` 的最小 UI 專案跑一輪 → 確認 S5.5 真的產圖、產 `-visual.md`、VERDICT 被 orchestrator 讀到
4. 故意拿掉預覽指令 → 確認回 `SKIPPED` 且不擋 sprint
