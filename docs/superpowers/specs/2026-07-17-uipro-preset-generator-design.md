# ui-ux-pro-max 整合：量身 preset 產生器 + anti-slop 禁用規則

日期：2026-07-17
狀態：已核可（使用者拍板：vendor 方式 + S0 設置棒時機）
來源：https://github.com/nextlevelbuilder/ui-ux-pro-max-skill（MIT）

## 背景與問題

UX Track C+B（2026-07-16 merge）已驗證能「抬高地板」，但 Track C 的
`templates/design-system.md` 是**一份寫死的 Stripe 風通用 preset**：儀表板、
工具站、行銷頁全套同一件衣服，不合身時產出品質就差。該檔開頭自己就承認
「資料密集後台這套會顯得鬆，換一份更緊的 preset 更合適」——但框架沒有給
「換」的工具。

ui-ux-pro-max-skill 是一台 preset 產生機：CSV 資料庫（84 風格、192 配色、
74 字體搭配、161 條產品類型→風格推理規則、98 條 UX 準則）+ 純標準庫 Python
BM25 搜尋，`--design-system` 一個指令依產品類型產出完整 design system 與
反模式清單。已實測離線可跑：以 "taiwan stock dip scanner data-dense
dashboard" 查詢，產出 Data-Dense Dashboard 風格 + 石板灰/股市綠色票 +
Fira Code/Fira Sans——與 Stripe 制服完全不同方向，證明價值。

**定位（期望管理）**：這仍是「抬地板」的延伸——把地板從「一件 Stripe 制服」
升級成「量身選過的制服」，不是變出 Lovable 級驚豔 UI（見
memory: project-ux-track-c-b 的驗證結論）。

## 設計

### 1. Vendor 層（dev-factory 源頭）

新增 `vendor/ui-ux-pro-max/`：

```
vendor/ui-ux-pro-max/
  LICENSE            # 上游 MIT LICENSE 原文
  README.md          # 來源 repo、抓取日期、上游 commit、手動同步方式
  scripts/           # core.py / design_system.py / search.py（純標準庫）
  data/              # 13 個 domain CSV（~1.2MB）
```

- **不含** 22 個 `stacks/*.csv`（per-stack 實作技巧，非 --design-system
  所需；保持精簡，日後有需要再加）。
- `install.sh` 的 `seed_project()` 新增一步：`cp -R` vendor 內容 →
  目標專案 `.claude/uipro/`，**無條件覆蓋**（是框架資料檔，使用者不會改；
  與 design-system.md 的保護策略不同，是刻意的）。
- agent 呼叫路徑固定為專案相對：`.claude/uipro/scripts/search.py`。

### 2. S0 設置棒（preset 生成，每專案至多一次）

- `templates/design-system.md` **首行**加出廠 marker：
  `<!-- dev-factory-default-preset -->`。
- `/sprint`（skills/sprint/SKILL.md）在「UX 強度判定」步驟選定/讀到 `full`
  時，檢查 `docs/design/design-system.md` 首行 marker：
  - **有 marker** → S1 之前插入一次性 **S0 設置棒**（派 ux-designer）。
  - **無 marker**（使用者已客製、或舊版安裝的既有專案）→ 跳過 S0，照舊。
- S0 派工內容（ux-designer，tools 補 `Bash`）：
  1. 讀 `docs/PROJECT_GOAL.md`，組查詢關鍵字：產品類型 + 產業 + 風格/密度
     詞（例 "fintech dashboard data-dense"）。
  2. 跑 `python3 .claude/uipro/scripts/search.py "<query>" --design-system
     -f markdown`；資料密集後台類加 `--density 8`，行銷頁類加
     `--density 3`。
  3. 把輸出**翻譯成三段式格式**（`## Design Tokens` / `## 元件` /
     `## 禁用規則`，agent 靠標題定位，不可改）：token 表換成生成值；元件段
     沿用出廠模板的骨架（按鈕/輸入框/卡片/表格/對話框/狀態呈現），依新
     token 與風格調整描述；**通用禁用規則（含 anti-slop 條）全數保留併入**，
     再附上該產品類型的反模式（來自輸出的 Avoid 段）。
  4. 寫回 `docs/design/design-system.md`，**移除 marker**（表示已量身，
     之後不再重生成）。
  5. 回報 orchestrator 選了什麼風格/色系，orchestrator 於收尾摘要告知
     使用者。
- **降級路徑**：`python3` 不存在或腳本失敗 → S0 回 SKIPPED，沿用出廠
  Stripe 預設（＝現行行為），不擋 sprint；收尾摘要註記。
- `templates/CLAUDE.md` 的劇本描述同步補 S0 一句。

### 3. Anti-slop 通用禁用規則（preset 無關，永遠保留）

`templates/design-system.md` 的「## 禁用規則」新增：

11. **emoji 不得當結構性圖示**（導覽、按鈕、狀態指示）。用同一家族的 SVG
    圖示（lucide/heroicons/phosphor 擇一）；同一層級不得混用 filled/outline，
    筆畫粗細須一致。
12. **hover/pressed 態不得造成版面位移**。用 color/opacity/shadow/transform
    表達，不得改變 layout bounds。
13. **未經 PROJECT_GOAL 定調，不得使用「AI 紫粉漸層」類配色**（generic AI
    產出的廉價感標誌）。
14. **可點擊元素必有 `cursor: pointer` 與 hover 回饋**。

- visual-reviewer 的機械式對照本來就逐條讀「## 禁用規則」→ 自動涵蓋，
  `agents/visual-reviewer.md` 不需結構性改動（至多在讀圖批判清單加一句
  「圖示一致性：放大截圖檢查是否 emoji/混家族」提示）。
- S0 翻譯規格明定生成檔必含這些通用條目（寫進派工 prompt 與 ux-designer.md）。

### 4. 既有專案遷移

- install.sh 對 design-system.md 的「不覆蓋」保護**不變**。
- 舊專案（如 tw-stock-dip-scanner）兩條路，寫進 README 升級註記：
  a. 手動把新 anti-slop 禁用規則貼進該專案的 design-system.md；
  b. 想換量身 preset → 把該檔重置為出廠模板（含 marker），下次 full sprint
     由 S0 重生成。

## 改動檔案清單

| 檔案 | 改動 |
|---|---|
| `vendor/ui-ux-pro-max/` | 新增（scripts ×3、data ×13、LICENSE、README） |
| `install.sh` | seed_project() 複製 vendor → `.claude/uipro/` |
| `templates/design-system.md` | 首行 marker + 禁用規則 11–14 |
| `templates/CLAUDE.md` | 劇本補 S0 一句 |
| `skills/sprint/SKILL.md` | UX 強度判定後插 S0 觸發邏輯與派工規格 |
| `agents/ux-designer.md` | tools 補 Bash + S0 任務章節 |
| `agents/visual-reviewer.md` | 讀圖清單補圖示一致性一句（微調） |
| `README.md` / `README.zh-TW.md` | vendor 來源註記 + 既有專案遷移註記 |

## 測試計畫

1. **install 煙霧測試**：install.sh 裝進 scratchpad 假專案 → 驗證
   `.claude/uipro/` 齊備、`python3 search.py "<query>" --design-system`
   離線可跑、templates 三段標題與 marker 存在。
2. **重跑保護**：對同一假專案重跑 install.sh → design-system.md 不被覆蓋、
   uipro 正常更新。
3. **S0 全流程**：屬 agent 行為，留給下次真實專案首次 full sprint 煙霧測試
   （同 B-048 驗證模式）。

## 非目標

- 不 vendor stacks CSV、不引入 MASTER.md/pages 覆寫機制（與
  docs/design/design-system.md 單一真理來源衝突）。
- 不把 Python 搜尋做成 sprint 中途的常駐查詢步驟（token 與複雜度不划算；
  生成只在 S0 跑一次）。
- 不承諾「驚豔 UIUX」——僅是更合身的地板。
