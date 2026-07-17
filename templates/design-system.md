<!-- dev-factory-default-preset -->
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

**陰影是主要的分隔手段，不是邊框。** 這是這套 preset 最關鍵的一條。

| Token | 值 | 用途 |
|---|---|---|
| `--shadow-sm` | `0 2px 5px -1px rgba(50,50,93,.25), 0 1px 3px -1px rgba(0,0,0,.3)` | 按鈕、輸入框 |
| `--shadow-md` | `0 6px 12px -2px rgba(50,50,93,.25), 0 3px 7px -3px rgba(0,0,0,.3)` | 卡片、下拉選單 |
| `--shadow-lg` | `0 13px 27px -5px rgba(50,50,93,.25), 0 8px 16px -8px rgba(0,0,0,.3)` | 對話框、彈出層 |
| `--shadow-focus` | `0 0 0 3px rgba(99,91,255,.35)` | 焦點環（a11y 必須） |

雙層陰影（一層散、一層緊）是 Stripe 質感的來源，不要簡化成單層。

## 元件

每個元件寫：長什麼樣（用上面的 token）、有哪些變體、什麼時候用。

### 按鈕
- **Primary**：`--color-primary` 底、白字、`--radius-md`、`--shadow-sm`、padding `--space-3` `--space-5`、`--text-body` 600。hover 升 `--color-primary-hover` 並把陰影升到 `--shadow-md`（Stripe 的按鈕會「浮起來」）。**一個畫面只能有一個 primary。**
- **Secondary**：白底、`--color-text` 字、`--shadow-sm`。次要動作。
- **Ghost**：無底無框、`--color-primary` 字。低調動作、工具列。
- **Danger**：`--color-danger` 底、白字。破壞性動作，且必須有確認步驟。
- 停用態：`--color-text-muted` 字 + `--color-bg-subtle` 底 + 無陰影 + `cursor: not-allowed`。

### 輸入框
`--radius-md`、`1px solid --color-border`、padding `--space-3`、`--text-body`。focus 時邊框轉 `--color-primary` 並加 `--shadow-focus`。錯誤時邊框 `--color-danger`，**錯誤訊息放在框下方**、`--text-small`、`--color-danger`——不要只靠紅框表達錯誤（a11y）。

### 卡片
白底、`--radius-lg`、`--shadow-md`、padding `--space-5`。**不加邊框**（陰影已經分隔了，加邊框是這套 preset 最常見的破壞）。可點擊的卡片 hover 升 `--shadow-lg`。

### 表格
表頭 `--text-caption` 大寫 + `--color-text-secondary`；列高至少 `--space-7`；分隔用 `1px --color-border` 底線（表格是**唯一**用邊框而非陰影分隔的地方）；整個表格包在卡片裡。

### 對話框
`--radius-xl`、`--shadow-lg`、padding `--space-6`、最大寬 480px（表單型）；遮罩 `rgba(10,37,64,.4)`。標題 `--text-h2`、動作鈕靠右下、primary 在最右。

### 狀態呈現
- **載入中**：骨架屏（`--color-bg-subtle` 底 + 微動畫），不要用轉圈圈佔整頁。
- **空狀態**：圖示 + `--text-h3` 標題 + `--text-body` 說明 + 一個 primary 動作。不要只寫「無資料」。
- **錯誤**：`--color-danger`，說明「發生什麼事」與「怎麼辦」，附重試動作。

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
9. **`--color-accent` 不用於一般 UI 元件**，只做漸層搭配與圖表點綴。
10. **不要擠。** 區塊間距低於 `--space-7` 通常是錯的——慷慨留白是這套 preset 的識別特徵。
11. **emoji 不得當結構性圖示**（導覽、按鈕、狀態指示、清單項目符號）。用同一家族的 SVG 圖示（lucide / heroicons / phosphor 擇一）；同一層級不得混用 filled 與 outline，筆畫粗細須一致。
12. **hover / pressed 態不得造成版面位移。** 回饋用 color / opacity / shadow / transform 表達，不得改變元素的 layout bounds（hover 時改 border 寬、字重、尺寸都是錯的）。
13. **未經 PROJECT_GOAL 定調，不得使用「AI 紫粉漸層」類配色。** 紫→粉大面積漸層是 generic AI 產出的廉價感標誌；漸層只能由本檔 token 表的色彩構成。
14. **可點擊元素必有 `cursor: pointer` 與 hover 回饋。** 看起來能點但毫無反應的元素是錯的。

> 規則 11–14 是**通用 anti-slop 條款**，與 preset 風格無關：整份換 preset 或由 S0 生成量身版本時，這四條必須原樣保留。
