# UX Track C + B Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 給 dev-factory 兩樣它現在完全沒有的東西——一份當作輸入約束的設計系統（設計師的替代品），和一隻能看見成品的眼睛（視覺回饋關）。

**Architecture:** 靜態 `design-system.md` 由 install 鋪進目標專案，ux-designer / developer / visual-reviewer 三棒共讀；新 `visual-reviewer` 一棒用 Bash + playwright CLI 截圖、Read 讀圖、對照設計系統批判，掛在 S5 後成為獨立的 S5.5 迴圈。兩者由正交於 governance profile 的 `UX 強度：light / full` 開關控制，預設 `light`（＝現狀，不動既有專案）。

**Tech Stack:** Markdown（agent 定義與範本）、Bash（install.sh）、playwright CLI（目標專案端，非 dev-factory 依賴）。

**Spec:** `docs/superpowers/specs/2026-07-16-ux-track-c-b-design.md`

## Global Constraints

- **這個 repo 沒有程式碼與測試框架**——產物全是 markdown 提示詞與一支 bash installer。因此沒有 RED/GREEN 測試循環；每個 task 的驗證是 **具體的 shell 指令 + 預期輸出**（grep / install smoke test）。不要為了套 TDD 而發明假測試。
- **dev-factory 是要被 install 進「別的專案」的框架。** 任何新依賴都是每個目標專案的安裝負擔。**不得引入 MCP 依賴。**
- **預設值一律 `light`**：既有專案跑起來行為必須與現在完全相同。任何讓 `light` 專案行為改變的實作都是 bug。
- **`UX 強度` 正交於 `治理 profile`**：profile 管 gate 嚴格度，UX 強度管 UX 深度。不得讓其中一個決定另一個。
- 所有新 gate 沿用既有護欄機制：`VERDICT:` 第一行、R-15-1 落檔鐵則、退回計數記在「執行狀態」區塊、計入總修復預算 6。
- 文件語言：繁體中文，與既有檔案一致。
- 每個 task 結束時 commit。

---

### Task 1: Stripe 風設計系統範本

這是 Track C 的全部內容，也是整個計畫裡唯一「有品味成分」的檔案。它必須**具體到可照抄**——寫抽象原則（「保持一致」「注意層級」）等於沒寫，agent 會照樣自由發揮。

**Files:**
- Create: `templates/design-system.md`

**Interfaces:**
- Produces: `docs/design/design-system.md`（install 後的路徑）。Task 3/4 的三棒 agent 會 Read 它；section 標題被 agent 定義引用，需固定為：`## Design Tokens`、`## 元件`、`## 禁用規則`。

- [ ] **Step 1: 寫 `templates/design-system.md`**

檔頭要聲明可換掉（避免它被當成不可動的聖旨）：

```markdown
# 設計系統（Design System）

> **這是 dev-factory 鋪進來的「預設品味」——Stripe 風。它是 UI 工作的輸入約束，不是建議。**
> 沒有設計師時，這份檔案就是設計師。ux-designer 依它寫規格、developer 依它實作、visual-reviewer 依它批判截圖。
>
> **整份可以換掉。** 這套的甜蜜點是行銷頁與中低密度產品介面；若你的專案是資料密集的後台表格，這套會顯得鬆，換一份更緊的 preset（Linear/Vercel 風）更合適。換掉時保持三個 section 標題不變（`## Design Tokens` / `## 元件` / `## 禁用規則`），agent 靠它們定位。

## Design Tokens

### 色彩

| Token | 值 | 用途 |
|---|---|---|
| `--color-primary` | `#635BFF` | 主要動作、連結、焦點環 |
| `--color-primary-hover` | `#7A73FF` | 主色 hover |
| `--color-primary-active` | `#5147E5` | 主色 pressed |
| `--color-accent` | `#00D4FF` | 漸層搭配色、圖表點綴（**不用於一般 UI 元件**） |
| `--color-text` | `#0A2540` | 標題與主要文字（深藍調，非純黑） |
| `--color-text-secondary` | `#425466` | 次要文字、說明 |
| `--color-text-muted` | `#8792A2` | 佔位符、停用態 |
| `--color-bg` | `#FFFFFF` | 主背景 |
| `--color-bg-subtle` | `#F6F9FC` | 次層背景、區塊分隔（**帶藍調的白，非純灰**） |
| `--color-border` | `#E3E8EE` | 邊框、分隔線 |
| `--color-success` | `#09825D` | 成功態 |
| `--color-warning` | `#BB5504` | 警告態 |
| `--color-danger` | `#DF1B41` | 錯誤、破壞性動作 |

### 間距

4px 基準。**只能取這個 scale 內的值**：

`--space-1: 4px` / `--space-2: 8px` / `--space-3: 12px` / `--space-4: 16px` / `--space-5: 24px` / `--space-6: 32px` / `--space-7: 48px` / `--space-8: 64px` / `--space-9: 96px`

區塊之間用 `--space-7` 以上；Stripe 風的特徵就是**慷慨的垂直節奏**，不要擠。

### 字級

字體：`Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`

| Token | size / line-height / weight | 用途 |
|---|---|---|
| `--text-display` | 48px / 1.16 / 700 | 首頁主標 |
| `--text-h1` | 32px / 1.25 / 600 | 頁標題 |
| `--text-h2` | 24px / 1.33 / 600 | 區塊標題 |
| `--text-h3` | 19px / 1.4 / 600 | 卡片標題 |
| `--text-body` | 16px / 1.6 / 400 | 內文 |
| `--text-small` | 14px / 1.5 / 400 | 次要說明 |
| `--text-caption` | 12px / 1.4 / 500 | 標籤、表格頭（常搭 `letter-spacing: 0.4px` + 大寫） |

級距跳躍要明顯、標題要重——這是 Stripe 風與工具風的主要區別之一。

### 圓角

`--radius-sm: 4px`（標籤、小徽章）/ `--radius-md: 8px`（按鈕、輸入框）/ `--radius-lg: 12px`（卡片）/ `--radius-xl: 16px`（對話框、大面板）/ `--radius-full: 9999px`（頭像、pill）

### 陰影

**陰影是主要的分隔手段,不是邊框。** 這是這套 preset 最關鍵的一條。

| Token | 值 | 用途 |
|---|---|---|
| `--shadow-sm` | `0 2px 5px -1px rgba(50,50,93,.25), 0 1px 3px -1px rgba(0,0,0,.3)` | 按鈕、輸入框 |
| `--shadow-md` | `0 6px 12px -2px rgba(50,50,93,.25), 0 3px 7px -3px rgba(0,0,0,.3)` | 卡片、下拉選單 |
| `--shadow-lg` | `0 13px 27px -5px rgba(50,50,93,.25), 0 8px 16px -8px rgba(0,0,0,.3)` | 對話框、彈出層 |
| `--shadow-focus` | `0 0 0 3px rgba(99,91,255,.35)` | 焦點環（a11y 必須） |

雙層陰影（一層散、一層緊）是 Stripe 質感的來源,不要簡化成單層。

## 元件

每個元件寫：長什麼樣（用上面的 token）、有哪些變體、什麼時候用。

### 按鈕
- **Primary**：`--color-primary` 底、白字、`--radius-md`、`--shadow-sm`、padding `--space-3` `--space-5`、`--text-body` 600。hover 升 `--color-primary-hover` 並把陰影升到 `--shadow-md`（Stripe 的按鈕會「浮起來」）。**一個畫面只能有一個 primary。**
- **Secondary**：白底、`--color-text` 字、`--shadow-sm`。次要動作。
- **Ghost**：無底無框、`--color-primary` 字。低調動作、工具列。
- **Danger**：`--color-danger` 底、白字。破壞性動作，且必須有確認步驟。
- 停用態：`--color-text-muted` 字 + `--color-bg-subtle` 底 + 無陰影 + `cursor: not-allowed`。

### 輸入框
`--radius-md`、`1px solid --color-border`、padding `--space-3`、`--text-body`。focus 時邊框轉 `--color-primary` 並加 `--shadow-focus`。錯誤時邊框 `--color-danger`,**錯誤訊息放在框下方**、`--text-small`、`--color-danger`——不要只靠紅框表達錯誤（a11y）。

### 卡片
白底、`--radius-lg`、`--shadow-md`、padding `--space-5`。**不加邊框**（陰影已經分隔了,加邊框是這套 preset 最常見的破壞）。可點擊的卡片 hover 升 `--shadow-lg`。

### 表格
表頭 `--text-caption` 大寫 + `--color-text-secondary`；列高至少 `--space-7`；分隔用 `1px --color-border` 底線（表格是**唯一**用邊框而非陰影分隔的地方）；整個表格包在卡片裡。

### 對話框
`--radius-xl`、`--shadow-lg`、padding `--space-6`、最大寬 480px（表單型）；遮罩 `rgba(10,37,64,.4)`。標題 `--text-h2`、動作鈕靠右下、primary 在最右。

### 狀態呈現
- **載入中**：骨架屏（`--color-bg-subtle` 底 + 微動畫），不要用轉圈圈佔整頁。
- **空狀態**：圖示 + `--text-h3` 標題 + `--text-body` 說明 + 一個 primary 動作。不要只寫「無資料」。
- **錯誤**：`--color-danger`,說明「發生什麼事」與「怎麼辦」,附重試動作。

## 禁用規則

違反這些的一律視為 CHANGES_REQUIRED：

1. **不得自創色值。** 只能用上面表格裡的 token。要新顏色 → 標 `⚠️ 需擴充 design system`。
2. **不得自創間距。** 只能取 `--space-*` scale 內的值。`padding: 13px` 是錯的。
3. **不得用邊框取代陰影分隔**（表格底線除外）。卡片加 `border` 是錯的。
4. **不得用單層陰影。** 雙層是這套質感的來源。
5. **一個畫面只能有一個 primary 按鈕。**
6. **不得只靠顏色傳達資訊**（a11y）。錯誤要有文字、狀態要有圖示或文案。
7. **焦點態不得移除。** `outline: none` 而沒補 `--shadow-focus` 是錯的。
8. **對比度**：正文對背景至少 4.5:1，大字至少 3:1（WCAG AA）。
9. **`--color-accent` 不用於一般 UI 元件**,只做漸層搭配與圖表點綴。
10. **不要擠。** 區塊間距低於 `--space-7` 通常是錯的——慷慨留白是這套 preset 的識別特徵。
```

- [ ] **Step 2: 驗證三個 section 標題存在（agent 定義靠它們定位）**

Run:
```bash
grep -c '^## Design Tokens$\|^## 元件$\|^## 禁用規則$' templates/design-system.md
```
Expected: `3`

- [ ] **Step 3: Commit**

```bash
git add templates/design-system.md
git commit -m "feat: Stripe 風設計系統範本（Track C 約束層）"
```

---

### Task 2: 播種——PROJECT_GOAL 新欄位 + install.sh 鋪檔

把 Task 1 的範本真的送進目標專案,並給它兩個開關欄位。這個 task 的交付物是「跑完 install 後,專案有了設計系統與開關」,可用 smoke test 獨立驗證。

**Files:**
- Modify: `templates/PROJECT_GOAL.md`（治理 profile 區塊後、技術約束區塊）
- Modify: `install.sh`（`seed_project()` 函式，約 line 86-96）

**Interfaces:**
- Consumes: `templates/design-system.md`（Task 1）
- Produces: `docs/design/design-system.md`、`docs/design/ux/screenshots/` 目錄、PROJECT_GOAL 的 `UX 強度` 與 `預覽指令` 兩欄。Task 3/4/5 全部依賴這兩欄的**精確欄位名**。

- [ ] **Step 1: `templates/PROJECT_GOAL.md` 加 `UX 強度` 區塊**

在「## 治理 profile」整段之後、「## 一句話」之前插入：

```markdown
## UX 強度
<light / full —— 與治理 profile **正交**：profile 管 gate 嚴格度，這欄管 UX 深度。留空則 `/sprint` 首次開跑會與 profile 一起問你一次（每專案一次）。>
- **light**（預設）：ux-designer 僅在有可見面時跑，產出 markdown 規格。無設計系統約束、無視覺關。純後端/CLI、或 UI 品質不是重點時用。
- **full**：ux-designer / developer / visual-reviewer 三棒共讀 `docs/design/design-system.md` 當硬約束；開發後多一道 **S5.5 視覺關**（截圖 → 對照設計系統批判 → 退回修）。UI 品質是產品成敗關鍵時用。
```

- [ ] **Step 2: `templates/PROJECT_GOAL.md` 的技術約束區塊加預覽指令**

把：
```markdown
## 技術約束 / 偏好
- <語言、框架、部署環境、必須整合的服務、不能用的東西>
```
改成：
```markdown
## 技術約束 / 偏好
- <語言、框架、部署環境、必須整合的服務、不能用的東西>
- **預覽指令**：<UX 強度=full 且有 UI 時必填。visual-reviewer 靠它起專案截圖。例：`npm run dev`，port 3000。留空 → 視覺關會回 SKIPPED。>
```

- [ ] **Step 3: `install.sh` 鋪設計系統與 screenshots 目錄**

在 `seed_project()` 裡，把 mkdir 那行的 `"$proj/docs/design/ux"` 之後補上 screenshots 子目錄，並加一行 cp。

mkdir 改成（注意 `docs/design/ux/screenshots`）：
```bash
  mkdir -p "$proj/docs/sprints" "$proj/docs/design/ux/screenshots" "$proj/docs/design/tech" \
           "$proj/docs/design/adr" "$proj/docs/design/review" "$proj/docs/retro" \
           "$proj/docs/discovery"
```

在 `[ -f "$proj/docs/discovery/rubric.md" ] || cp ...` 那行之後補：
```bash
  [ -f "$proj/docs/design/design-system.md" ] || cp "$FACTORY_DIR/templates/design-system.md" "$proj/docs/design/design-system.md"
```

（用 `[ -f ] ||` 而非無條件 cp——設計系統是**使用者會改的檔**,重跑 install 不能洗掉他換過的 preset。這與 adr/sprint 範本的無條件 cp 不同,是刻意的。）

echo 那行改成：
```bash
  echo "  ✓ docs/ 骨架（PROJECT_GOAL、backlog、DIRECTION、discovery/rubric、design-system、範本）"
```

- [ ] **Step 4: `install.sh` 更新角色數提示**

`copy_core()` 裡的 echo（約 line 72）目前寫「建造 10 角」，加了 visual-reviewer 後是 11：

```bash
  echo "  ✓ agents → $claude_dir/agents/（建造 11 角含合併驗證關 reviewer + 視覺關 visual-reviewer + discovery 3 角 explorer/critic/shaper）"
```

- [ ] **Step 5: Smoke test——跑一次 seed 驗證**

Run:
```bash
rm -rf /tmp/df-smoke && mkdir -p /tmp/df-smoke && ./install.sh --seed-only /tmp/df-smoke >/dev/null && \
  test -f /tmp/df-smoke/docs/design/design-system.md && echo "design-system OK" && \
  test -d /tmp/df-smoke/docs/design/ux/screenshots && echo "screenshots dir OK" && \
  grep -q '^## UX 強度$' /tmp/df-smoke/docs/PROJECT_GOAL.md && echo "UX 強度欄 OK" && \
  grep -q '預覽指令' /tmp/df-smoke/docs/PROJECT_GOAL.md && echo "預覽指令欄 OK"
```
Expected: 四行 OK 全出現

- [ ] **Step 6: 驗證重跑不覆蓋使用者改過的設計系統**

Run:
```bash
echo "USER EDIT" >> /tmp/df-smoke/docs/design/design-system.md && \
  ./install.sh --seed-only /tmp/df-smoke >/dev/null && \
  grep -q "USER EDIT" /tmp/df-smoke/docs/design/design-system.md && echo "不覆蓋 OK"
```
Expected: `不覆蓋 OK`

- [ ] **Step 7: Commit**

```bash
git add templates/PROJECT_GOAL.md install.sh
git commit -m "feat: 播種 design-system 與 UX 強度/預覽指令欄位"
```

---

### Task 3: `visual-reviewer` agent（Track B 的眼睛）

**Files:**
- Create: `agents/visual-reviewer.md`

**Interfaces:**
- Consumes: `docs/design/design-system.md`(Task 1/2)、PROJECT_GOAL 的「預覽指令」欄(Task 2)
- Produces: `docs/sprints/sprint-<N>-visual.md`（第一行 `VERDICT: PASS|CHANGES_REQUIRED|SKIPPED`）、截圖於 `docs/design/ux/screenshots/sprint-<N>/`。Task 5 的 orchestrator 讀這個 VERDICT；Task 4 的 developer 讀這份報告修。

- [ ] **Step 1: 寫 `agents/visual-reviewer.md`**

frontmatter 的 `model: opus` 是刻意的——這一棒的全部價值就是視覺判斷力,降級等於自廢 Track B。

```markdown
---
name: visual-reviewer
description: 視覺回饋關（gate）。渲染實際畫面、截圖、對照設計系統與 UX 規格批判視覺品質與 a11y，不過退回 developer。S5.5 被呼叫（僅在 UX 強度=full 且本輪有使用者可見面時）。
tools: Read, Write, Edit, Bash, Glob
model: opus
---

你是**視覺回饋關**（gatekeeper）。你是整條管線裡**唯一真的看過成品長什麼樣**的角色——其他每一棒都只讀得到文字。這就是你存在的理由：markdown 規格說「卡片有適當間距」時，只有你能看出它實際上擠成一團。

> **何時會被派**：`UX 強度=full` 且本輪有使用者可見面。`light` 專案不會派你。

## 啟動時先讀
- `docs/LESSONS.md` 的通用區 + `visual-reviewer` 小節
- `docs/design/design-system.md`（**你的判定依據**——token、元件、禁用規則）
- `docs/design/ux/sprint-<N>-ux.md`（本輪該長什麼樣、有哪些狀態）
- `docs/sprints/sprint-<N>.md`（驗收標準裡與可見面相關的條目）
- `docs/PROJECT_GOAL.md` 的「技術約束 / 偏好 → 預覽指令」（怎麼起專案）

## 流程

### 1. 起專案
用 Bash 依「預覽指令」啟動 dev server（背景跑）。等它真的起來再截圖——sever 還沒 ready 就截會拿到空白頁，那是假訊號。

**起不來就停**：不要硬試超過兩次。寫報告 `VERDICT: SKIPPED` 說明卡在哪（缺預覽指令 / 裝不起來 / port 衝突 / build 失敗），回報 orchestrator。**不擋 sprint,但也不准靜默跳過。**

### 2. 截圖
用 Bash 跑 playwright CLI（目標專案端工具，非本框架依賴）：
```
npx --yes playwright screenshot --viewport-size=1280,800 "http://localhost:<port>/<path>" "docs/design/ux/screenshots/sprint-<N>/<screen>-desktop.png"
npx --yes playwright screenshot --viewport-size=390,844  "http://localhost:<port>/<path>" "docs/design/ux/screenshots/sprint-<N>/<screen>-mobile.png"
```
要涵蓋：**每個本輪動到的畫面 × 桌機/行動兩個斷點**。UX 規格裡列的狀態（空 / 載入 / 錯誤）能重現的也要截——若需要特定資料或路由才能重現，用 playwright 腳本（`npx playwright test` 或 `node` + `playwright` API）走流程再截，別為了省事只截 happy path。

截不到某個狀態 → 在報告裡標明「未覆蓋：<狀態>，原因：<…>」，不要假裝檢查過。

### 3. 讀圖批判
**用 `Read` 逐張讀截圖**（Read 能直接看圖）。沒讀圖就寫報告 = 這一棒沒做。

對照 `design-system.md` 逐項查：
1. **禁用規則**：逐條對照該檔的「## 禁用規則」——自創色值/間距、卡片加邊框、單層陰影、多個 primary、只靠顏色傳達資訊、移除焦點態、對比不足、間距太擠。這是**機械式對照**，不是憑感覺。
2. **Token 遵循**：色彩/間距/字級/圓角/陰影是不是真的取自 token？（看得出來的偏差就抓，必要時 Grep 原始碼確認）
3. **資訊層級**：主要動作看得出來是主要的嗎？視線落點對嗎？標題與內文的級距拉開了嗎？
4. **版面**：對齊、疏密、留白節奏。有沒有孤兒元素、破版、溢出？
5. **RWD**：行動斷點有沒有擠壓、水平捲動、觸控目標過小（< 44px）？
6. **a11y**：對比度、焦點態、錯誤是否有文字而不只有紅框。
7. **對照 UX 規格**：實作出來的跟 `sprint-<N>-ux.md` 說的一致嗎？規格說有的狀態，做出來了嗎？

**判定尺度**：你是 gate 不是 art director。抓的是**違反設計系統的客觀問題**與**明顯的視覺缺陷**，不是個人品味偏好。「我覺得這個藍色比較好看」不是 issue；「這個藍色不在 token 表裡」是。

### 4. 收工
關掉你起的 dev server（別留背景 process）。

## 產出：`docs/sprints/sprint-<N>-visual.md`
- **報告第一行固定**：`VERDICT: PASS` / `VERDICT: CHANGES_REQUIRED` / `VERDICT: SKIPPED`
- 逐條問題標：**嚴重度**、**哪張截圖**（路徑）、**違反哪條禁用規則或哪個 token**、**要改什麼**、**哪個檔案**（供 orchestrator 給 developer 窄 context）
- 列出本輪截了哪些畫面 × 斷點 × 狀態，以及**未覆蓋的與原因**
- **放行門檻**：無禁用規則違反、無明顯視覺缺陷、與 UX 規格一致 → PASS。否則 CHANGES_REQUIRED。
- 純主觀的改善建議可以寫，但標「建議（不擋關）」，不列入 CHANGES_REQUIRED。

## 回報 orchestrator
PASS（進 S6 驗證關）/ CHANGES_REQUIRED（附問題清單與**被點名的檔案清單**，供窄 context 退回）/ SKIPPED（附原因）。修復迴圈上限 2 輪，達上限仍不過就升級使用者。

## 報告落檔鐵則（R-15-1）
你有 `Write` 工具；本棒最後一步 **MUST** 用 `Write` 把報告落檔至 `docs/sprints/sprint-<N>-visual.md`。**不得聲稱 harness 限制而跳過寫檔**；若真遇寫入錯誤，須在回報中明確引用錯誤訊息，交 orchestrator 代錄。報告檔缺席＝本棒未完成。SKIPPED 也一樣要落檔。
```

- [ ] **Step 2: 驗證 frontmatter 與 VERDICT 三態齊備**

Run:
```bash
head -6 agents/visual-reviewer.md && \
  grep -o 'VERDICT: PASS\|VERDICT: CHANGES_REQUIRED\|VERDICT: SKIPPED' agents/visual-reviewer.md | sort -u
```
Expected: frontmatter 有 `name: visual-reviewer` / `tools: Read, Write, Edit, Bash, Glob` / `model: opus`；三個 VERDICT 狀態各列出一次（用 `-o` 而非 `-c`——三態寫在同一行，`-c` 數行數會誤判）

- [ ] **Step 3: Commit**

```bash
git add agents/visual-reviewer.md
git commit -m "feat: visual-reviewer agent（Track B 視覺回饋關）"
```

---

### Task 4: Track C 消費端——ux-designer 與 developer

設計系統只有在**有人真的照它做、有人真的查**時才是約束。Task 3 做了「查」，這個 task 做「照它做」。

**Files:**
- Modify: `agents/ux-designer.md`（啟動時先讀區塊、產出區塊、原則區塊）
- Modify: `agents/developer.md`（啟動時先讀區塊、被退回區塊）

**Interfaces:**
- Consumes: `docs/design/design-system.md`(Task 1/2)、`docs/sprints/sprint-<N>-visual.md`(Task 3)
- Produces: 無新檔；ux-designer 的 `⚠️ 需擴充 design system` 標記由 consistency-reviewer 既有的「掃描 `⚠️`」機制接住（不需改 consistency-reviewer）。

- [ ] **Step 1: `agents/ux-designer.md` 加設計系統約束**

「## 啟動時先讀」清單最前面加一條：
```markdown
- `docs/design/design-system.md`（**若 UX 強度=full：這是硬約束，不是參考**。你的規格只能用這份檔裡既有的 token 與元件。檔案不存在或 UX 強度=light → 略過本條，照舊寫規格。）
```

「## 產出」的必含清單，把「**畫面與元件**」那條改成：
```markdown
- **畫面與元件**：每個畫面的版面、主要元件、資訊層級。**UX 強度=full 時：一律引用 `design-system.md` 的 token 名與元件名**（例「主要動作用 Primary 按鈕、卡片間距 `--space-5`」），不要用「適當的間距」「柔和的藍」這種無法驗證的描述——visual-reviewer 會拿 token 表逐項對照你的規格。
```

「## 原則」區塊加一條：
```markdown
- **不得自創設計系統外的東西**（UX 強度=full 時）。需要 token 表沒有的顏色/間距/元件 → 標 `⚠️ 需擴充 design system：<要什麼、為什麼現有的不夠>`，交 consistency-reviewer 裁決。**不要自己發明一個色值就用下去**——那正是設計系統要防的事。
```

- [ ] **Step 2: `agents/developer.md` 加 token 實作紀律**

「## 啟動時先讀」的 `docs/design/ux/sprint-<N>-ux.md（若涉及介面）` 那條之後加：
```markdown
- `docs/design/design-system.md`（**若涉及介面且 UX 強度=full**：實作時的硬約束。色彩/間距/字級/圓角/陰影一律取自它的 token，不自創值；並遵守其「## 禁用規則」。S5.5 視覺關會拿它逐條查你的成品。）
```

「## 若被驗證關退回」區塊之後，新增一個平行區塊：
```markdown
## 若被視覺關（S5.5 visual-reviewer）退回
讀 `docs/sprints/sprint-<N>-visual.md`。處置與上面的驗證關退回**同構**：窄 context（只碰報告點名的檔）、不盲從先驗證每條是否成立、只修被點名的問題。

差別在於：
- 視覺 issue 通常**沒有失敗測試可寫**（「卡片加了邊框」不是測試抓得到的）。這類 issue 照報告直接修，不必硬套 TDD 的 RED 步驟；但若修動到有測試覆蓋的邏輯，仍照 TDD。
- 每條 issue 都會標明違反了 `design-system.md` 的哪條規則或哪個 token——**照那條規則修，不要自己另想一套視覺解法**。
- 標「建議（不擋關）」的項目**不用改**，它們不是退回原因。
```

- [ ] **Step 3: 驗證兩個 agent 都指向設計系統**

Run:
```bash
grep -l 'design-system.md' agents/ux-designer.md agents/developer.md agents/visual-reviewer.md
```
Expected: 三個檔名全部列出

- [ ] **Step 4: Commit**

```bash
git add agents/ux-designer.md agents/developer.md
git commit -m "feat: ux-designer 與 developer 依設計系統約束工作"
```

---

### Task 5: Orchestrator 劇本——UX 強度判定 + S5.5 迴圈

這是把前面四個 task 接起來、真的會跑的地方。

**Files:**
- Modify: `skills/sprint/SKILL.md`（開跑前 §2、劇本 S2/S5 之後、Gate 與停止規則）
- Modify: `templates/sprint-log-template.md`（階段計畫、執行狀態）

**Interfaces:**
- Consumes: PROJECT_GOAL 的 `UX 強度` 欄(Task 2)、`visual-reviewer` agent(Task 3)
- Produces: S5.5 階段的派工與計數規則；sprint 主檔「執行狀態」區塊的 S5.5 條目與 `0/2` 計數欄。

- [ ] **Step 1: `skills/sprint/SKILL.md` 的開跑前 §2 併入 UX 強度提問**

在「2. **治理 profile 判定（HUMAN GATE，每專案問一次）**」整段之後、「3. **決定 N 與續跑判定**」之前，插入新的一步（後續編號順延為 4、5、6）：

```markdown
2b. **UX 強度判定（同一次 HUMAN GATE，每專案問一次）**：讀 `docs/PROJECT_GOAL.md` 是否已有「UX 強度：light / full」欄位。
   - **已設** → 沿用，不再問。
   - **未設** → **與 profile 同一次問**（不要分兩次打擾使用者）。依專案是否以 UI 為主要價值來源建議一個：
     - **`light`**（預設）：純後端/CLI/資料專案，或 UI 只是薄殼、品質不是重點。＝現行行為。
     - **`full`**：UI 品質是產品成敗關鍵（面向終端使用者的產品、行銷頁、需要「看起來專業」的東西）。啟用設計系統硬約束 + S5.5 視覺關。**成本**：多一棒 opus 視覺關 + 可能的退回迴圈。
   - 選定後把該欄位代寫進 `docs/PROJECT_GOAL.md`。**與治理 profile 正交**——profile 管 gate 嚴格度，UX 強度管 UX 深度，兩者互不決定對方（內部工具可以 lean + full；後端服務可以 max + light）。
   - 若選 `full`，順帶確認 PROJECT_GOAL 的「技術約束 → 預覽指令」有填；沒填就一起問（visual-reviewer 靠它起專案；缺了視覺關只能回 SKIPPED）。
```

- [ ] **Step 2: `skills/sprint/SKILL.md` 的 S2 標註設計系統**

「**S2. UX 設計**（有使用者可見面才跑）」那行後面補一句：
```markdown
   - UX 強度=`full` → 派工 prompt 標明「**本專案 UX 強度=full：`docs/design/design-system.md` 是硬約束，只能用它既有的 token 與元件；缺的標 `⚠️ 需擴充 design system`**」。
```

- [ ] **Step 3: `skills/sprint/SKILL.md` 插入 S5.5 劇本**

在「**S5. 開發**」與「**S6. 驗證關（形態依 profile）**」之間插入：

```markdown
**S5.5 視覺關**（`UX 強度=full` **且**本輪有使用者可見面才派）→ `subagent_type: visual-reviewer`。產 `docs/sprints/sprint-<N>-visual.md`。
   - 派工 prompt 要給：sprint 編號 N、預覽指令（取自 PROJECT_GOAL）、要讀的檔（`design-system.md`、`sprint-<N>-ux.md`、`sprint-<N>.md`）、要寫的檔。
   - `PASS` → 進 S6。
   - `CHANGES_REQUIRED` → 窄 context 退回 developer（附報告點名的檔案清單），修完重跑 S5.5。**上限 2 輪**，仍不過升級使用者。
   - `SKIPPED`（起不來/缺預覽指令）→ **不擋關，直接進 S6**，但要把原因記進「執行狀態」區塊，並在收尾摘要告訴使用者「本輪視覺關未執行，原因：<…>」。連續兩個 sprint SKIPPED → 收尾時建議使用者修好預覽指令，否則 Track B 形同虛設。
   - UX 強度=`light`，或本輪無使用者可見面 → 跳過本步（不派）。
```

- [ ] **Step 4: `skills/sprint/SKILL.md` 的迴圈計數規則補 S5.5**

「## Gate 與停止規則（重要）」的「**迴圈計數規則**」那條，把括號內容補上視覺關：
```markdown
- **迴圈計數規則**：各 gate 的退回計數**獨立且不重置**（一致性 2 / **視覺關 2** / 驗證關 3）。另設 **sprint 總修復預算 6 次**：任何 gate（一致性/視覺關/驗證關各區塊）的退回都累計，達 6 次即停下升級使用者（防 gate 之間互彈空轉）。所有計數記在「執行狀態」區塊，不憑記憶。
```

- [ ] **Step 5: `skills/sprint/SKILL.md` 的 gate 報告後置驗證補 `-visual.md`**

最後一節「## Gate 報告檔後置驗證（R-15-1…）」的路徑清單裡加入 `-visual.md`：
```markdown
每派一個 gate（一致性/**視覺關**/合併 reviewer/QA/資安/飄移）並收到回報後，orchestrator **必須先確認對應報告檔已存在**（Read/ls 對應 docs 路徑：`-review.md` / `-consistency.md` / `-visual.md` / `-qa.md` / `-security.md` / `-drift.md`）再推進下一階段。
```
（該節其餘文字不動。）

- [ ] **Step 6: `skills/sprint/SKILL.md` 的收尾摘要格式補視覺關**

「## 給使用者的收尾摘要格式」那行，在「驗證關結果（功能・資安・飄移）」後面插入「/ **視覺關結果（PASS/SKIPPED＋原因）**」。

- [ ] **Step 7: `templates/sprint-log-template.md` 的階段計畫加 UX 強度**

「## 階段計畫」區塊的「- 治理 profile」那行之後加：
```markdown
- UX 強度：<light / full，取自 PROJECT_GOAL> —— full 且有可見面 → 跑 S5.5 視覺關
```

- [ ] **Step 8: `templates/sprint-log-template.md` 的執行狀態加 S5.5**

「- [ ] S5 開發」與「- [ ] S6 驗證關」之間插入：
```markdown
- [ ] S5.5 視覺關（UX 強度=light 或無可見面 → 跳過）— 退回次數：0/2
```
並把「- 分支」那行改成：
```markdown
- 分支：`sprint-<N>`　profile：<lean/standard/max>　UX 強度：<light/full>
```

- [ ] **Step 9: 驗證劇本與範本一致**

Run:
```bash
grep -c 'S5.5' skills/sprint/SKILL.md templates/sprint-log-template.md && \
  grep -q 'visual-reviewer' skills/sprint/SKILL.md && echo "派工 OK" && \
  grep -q '0/2' templates/sprint-log-template.md && echo "計數欄 OK"
```
Expected: 兩個檔的 S5.5 計數都 ≥1，且兩行 OK

- [ ] **Step 10: Commit**

```bash
git add skills/sprint/SKILL.md templates/sprint-log-template.md
git commit -m "feat: orchestrator 劇本加入 UX 強度判定與 S5.5 視覺關"
```

---

### Task 6: 文件同步

機制做完了但文件沒跟上 = 使用者不知道有這功能，等於沒做。

**Files:**
- Modify: `templates/CLAUDE.md`（治理 profile 段、你的角色段、自主邊界 (f)）
- Modify: `docs/PIPELINE.md`（建造管線流程圖、角色與產物表、設計理念、護欄）
- Modify: `README.md`（內容樹的角色數、運作原理、客製）

**Interfaces:**
- Consumes: 全部前面的 task（描述它們）
- Produces: 無（純文件）

- [ ] **Step 1: `templates/CLAUDE.md` 加 UX 強度說明**

「## 治理 profile（決定成本，每專案問一次）」整段之後插入：
```markdown
## UX 強度（決定 UI 品質深度，每專案問一次）
`docs/PROJECT_GOAL.md` 另有一個「UX 強度」欄位，**與治理 profile 正交**（profile 管 gate 嚴格度，這欄管 UX 深度）：
- **light**（預設）：現行行為——ux-designer 僅在有可見面時跑，產 markdown 規格。
- **full**：`docs/design/design-system.md`（install 鋪的 Stripe 風預設，可整份換掉）成為 ux-designer/developer 的**硬約束**；開發後多一道 **S5.5 視覺關**——`visual-reviewer` 起專案、截圖、讀圖、對照設計系統批判，不過退回 developer。這是「沒有設計師也能有品味」的機制：品味 = 約束 + 回饋。
- full 需要 PROJECT_GOAL 的「技術約束 → 預覽指令」（例 `npm run dev` port 3000），visual-reviewer 靠它起專案；沒填視覺關只能回 SKIPPED。
若留空，`/sprint` 首次開跑會與 profile **同一次**問我。
```

「## 你的角色」段的 standard 序列那句，把 `developer → 驗證關` 改成 `developer → （visual-reviewer，UX 強度=full 且有可見面才跑）→ 驗證關`。

「## 自主邊界」的 (f) 那條改成：
```markdown
  (f) **本專案首次開跑、治理 profile 或 UX 強度未設** → 建議一組讓我選（**同一次問完**，每專案一次）。
```

- [ ] **Step 2: `docs/PIPELINE.md` 流程圖加 S5.5**

建造管線的 ASCII 圖裡，`S5. 開發` 與 `S6. 驗證關` 之間插入視覺關，並標明它是 full 專屬。把圖中這段：
```
                            S5. 開發 ◄──────────────┐
                                       ▼            │ CHANGES_REQUIRED
              S6. 驗證關（形態依 profile）──────────┤ 退回 S5（窄context，上限3輪）
```
改成：
```
                            S5. 開發 ◄──────────────┐
                                       ▼            │
                    S5.5 視覺關（UX 強度=full）─────┤ CHANGES_REQUIRED
                     截圖→對照 design-system→批判   │ 退回 S5（窄context，上限2輪）
                                       ▼ PASS/SKIPPED
              S6. 驗證關（形態依 profile）──────────┤ 退回 S5（窄context，上限3輪）
```

- [ ] **Step 3: `docs/PIPELINE.md` 角色表加 visual-reviewer**

「## 角色與產物」表格的 S5 與 S6 之間插入一列：
```markdown
| S5.5 | **visual-reviewer** | `sprints/sprint-N-visual.md` + `design/ux/screenshots/sprint-N/` | ✅ | UX 強度=`full` 且有可見面 |
```

- [ ] **Step 4: `docs/PIPELINE.md` 加「隨 profile 伸縮」段落的 UX 強度說明**

「**流程隨「治理 profile」伸縮**」那段清單之後補一段：
```markdown
**另有正交的「UX 強度」開關**（light/full，同樣每專案問一次）：`full` 讓 `docs/design/design-system.md` 成為 UX/開發的硬約束，並在 S5 後加一道 **S5.5 視覺關**（截圖 → 對照設計系統批判 → 退回）。profile 管 gate 嚴格度，UX 強度管 UX 深度，兩者互不決定對方。
```

- [ ] **Step 5: `docs/PIPELINE.md` 設計理念加一條**

「## 設計理念」清單末尾加：
```markdown
- **品味 = 約束 + 回饋，不是 prompt**：沒有設計師時，`design-system.md` 就是設計師——它是 UI 工作的**輸入約束**（ux-designer 只能用既有 token、developer 照 token 實作），不是事後檢查表。而 S5.5 視覺關是整條管線裡**唯一真的看過成品**的一棒：其他角色都只讀得到文字，只有它能發現「規格說適當間距、實際擠成一團」。兩者缺一不可——研究顯示有視覺 critic 的迭代帶來 +17.8% 品質，沒 critic 的純重新生成只有 +1.5%。
```

- [ ] **Step 6: `README.md` 更新角色數與說明**

內容樹那行改成：
```markdown
├── agents/          14 個角色 subagent（建造11：含合併驗證關 reviewer + 視覺關 visual-reviewer + discovery 3: explorer/critic/shaper）
```

`/sprint` 那條的流程序列，把 `開發 → 驗證關` 改成 `開發 → 視覺關 → 驗證關`。

templates 那行加入 design-system：
```markdown
├── templates/       CLAUDE.md 契約 + PROJECT_GOAL/backlog/DIRECTION/LESSONS/rubric/ADR/sprint/design-system 範本
```

「## 運作原理（重點）」清單裡，「治理 profile」那條之後加：
```markdown
- **UX 強度（UI 品質主鈕，正交於 profile）**：`light`（預設）＝現行行為；`full` 讓 `docs/design/design-system.md`（鋪進來的 Stripe 風預設，可整份換）成為 UX/開發的**硬約束**，並加一道 **S5.5 視覺關**——visual-reviewer 起專案截圖、讀圖、對照設計系統批判、不過退回。**沒有設計師也能有品味**靠的是這個：品味 = 約束 + 回饋，不是把「請做得好看」寫進 prompt。
```

「## 客製」清單加一條：
```markdown
- **不喜歡預設的視覺風格** → 整份換掉 `docs/design/design-system.md`。預設是 Stripe 風（暖中性色、慷慨留白、分層陰影、彩度主色），適合面向使用者的產品；資料密集的後台換成更緊的 Linear/Vercel 風更合適。換時保持 `## Design Tokens` / `## 元件` / `## 禁用規則` 三個 section 標題不變（agent 靠它們定位）。install 重跑**不會**覆蓋你改過的設計系統。
```

- [ ] **Step 7: 驗證文件一致性**

Run:
```bash
grep -q 'S5.5' docs/PIPELINE.md && grep -q 'visual-reviewer' docs/PIPELINE.md && echo "PIPELINE OK"; \
grep -q 'UX 強度' templates/CLAUDE.md && echo "CLAUDE OK"; \
grep -q '14 個角色' README.md && grep -q 'design-system' README.md && echo "README OK"; \
ls agents/*.md | wc -l
```
Expected: 三行 OK 全出現；agent 檔數 = `14`

- [ ] **Step 8: Commit**

```bash
git add templates/CLAUDE.md docs/PIPELINE.md README.md
git commit -m "docs: 文件同步 UX 強度與 S5.5 視覺關"
```

---

### Task 7: 端到端驗證

前六個 task 各自驗證了自己。這個 task 驗證的是**它們接起來真的成立**，以及最重要的一條：**沒有把既有的 light 專案弄壞**。

**Files:**
- 無（純驗證；若發現問題則修對應檔案）

- [ ] **Step 1: 全新安裝 smoke test**

Run:
```bash
rm -rf /tmp/df-e2e && mkdir -p /tmp/df-e2e && ./install.sh /tmp/df-e2e 2>&1 | tail -5 && \
  test -f /tmp/df-e2e/.claude/agents/visual-reviewer.md && echo "✓ visual-reviewer 有裝到" && \
  test -f /tmp/df-e2e/docs/design/design-system.md && echo "✓ design-system 有鋪到" && \
  test -d /tmp/df-e2e/docs/design/ux/screenshots && echo "✓ screenshots 目錄" && \
  ls /tmp/df-e2e/.claude/agents/*.md | wc -l
```
Expected: 三個 ✓ 全出現；agent 數 = `14`

- [ ] **Step 2: 驗證 light 不回歸——UX 強度未設時預設行為不變**

檢查劇本裡 S5.5 的觸發條件是否**嚴格**要求 `full`（欄位留空/不存在時不得觸發）。

Run:
```bash
grep -n 'S5.5' skills/sprint/SKILL.md
```
Expected: 派工條件明確寫「`UX 強度=full` **且** 本輪有使用者可見面才派」；並有一句「UX 強度=`light`，或本輪無使用者可見面 → 跳過本步（不派）」。**若條件寫得含糊（例如只寫「有可見面就派」），這是 bug，回去修 Task 5 Step 3。**

- [ ] **Step 3: 驗證交叉引用不斷鏈**

design-system 的三個 section 標題被 agent 引用；visual-reviewer 的報告路徑被 orchestrator 引用。確認沒有拼錯。

Run:
```bash
grep -q '^## Design Tokens$' templates/design-system.md && \
  grep -q '^## 元件$' templates/design-system.md && \
  grep -q '^## 禁用規則$' templates/design-system.md && echo "✓ section 標題" ; \
grep -q 'sprint-<N>-visual.md' agents/visual-reviewer.md && \
  grep -q 'visual.md' skills/sprint/SKILL.md && echo "✓ 報告路徑一致" ; \
grep -q '禁用規則' agents/visual-reviewer.md && echo "✓ visual-reviewer 引用禁用規則"
```
Expected: 三個 ✓ 全出現

- [ ] **Step 4: 清理**

Run:
```bash
rm -rf /tmp/df-smoke /tmp/df-e2e
```

- [ ] **Step 5: 更新 memory**

`project-ux-track-c-b.md` 記的是「NEXT WORK」，實作完就過期了。改寫成已完成狀態（或依 memory 規則，若已無後續價值則刪除並更新 `MEMORY.md` 索引）。`reference-ai-ui-taste-research.md` 保留——它是研究結論，仍有參考價值。

- [ ] **Step 6: Commit（若 Step 1-3 有修到東西）**

```bash
git add -A && git commit -m "fix: 端到端驗證發現的問題"
```
（無修改則跳過。）

---

## 後續（不在本計畫內）

- **實跑驗證**：本計畫只驗證「機制裝得起來、引用不斷鏈」。真正的驗證是拿一個 `full` 的最小 UI 專案跑一輪，確認 S5.5 真的產圖、批判有品質、退回迴圈會收斂。這需要一個真的目標專案，屬於下一步。
- 視覺回歸比對（跨 sprint 截圖 diff）、多 preset 切換機制、Track A（Figma）、Lovable 整合——見 spec 的「不做（YAGNI）」。
