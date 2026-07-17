# ui-ux-pro-max 整合（量身 preset 產生器 + anti-slop 規則）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 ui-ux-pro-max 的設計資料庫 vendor 進 dev-factory，讓首次 full sprint 由 S0 設置棒依產品類型生成量身 design-system.md，並在出廠模板加入四條通用 anti-slop 禁用規則。

**Architecture:** 資料與腳本 vendor 在 dev-factory 源頭的 `vendor/ui-ux-pro-max/`，install 時鋪到目標專案 `.claude/uipro/`；生成邏輯掛在 `/sprint` 就緒判定的 UX 強度步驟（marker 偵測、每專案至多一次），由 ux-designer 以 Bash 跑純標準庫 Python 腳本後翻譯成三段式格式。

**Tech Stack:** bash（install.sh）、Python 3 標準庫（vendored 腳本，不修改上游碼）、markdown（agent/skill/template 定義）。

**Spec:** `docs/superpowers/specs/2026-07-17-uipro-preset-generator-design.md`

## Global Constraints

- 上游來源固定為 `https://github.com/nextlevelbuilder/ui-ux-pro-max-skill`（MIT），vendor 時記錄抓取當下的 upstream commit SHA。
- **不 vendor** `data/stacks/*.csv`（22 檔）、不 vendor 上游 templates/tests。
- 上游 Python 腳本**原樣 vendor，不修改**（日後同步才不會衝突）。
- design-system.md 的三個 section 標題（`## Design Tokens` / `## 元件` / `## 禁用規則`）與出廠 marker `<!-- dev-factory-default-preset -->`（首行）是 agent 定位契約，所有產出都必須遵守。
- 出廠模板的禁用規則 11–14 為通用 anti-slop 條款：任何 preset 更換 / S0 生成都必須原樣保留。
- install.sh 對既有 `docs/design/design-system.md` 的不覆蓋保護**不得**被破壞；`.claude/uipro/` 則是無條件更新。
- 所有工作在 `~/Desktop/dev-factory`（源頭 repo）main 分支直接進行，每個 task 一個 commit，commit 訊息結尾附 `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`。
- 煙霧測試一律在 scratchpad 假專案目錄進行，不污染真實專案。

---

### Task 1: Vendor 上游資料與腳本

**Files:**
- Create: `vendor/ui-ux-pro-max/LICENSE`
- Create: `vendor/ui-ux-pro-max/README.md`
- Create: `vendor/ui-ux-pro-max/scripts/{core.py,design_system.py,search.py}`
- Create: `vendor/ui-ux-pro-max/data/*.csv`（13 檔，見下）

**Interfaces:**
- Produces: `vendor/ui-ux-pro-max/scripts/search.py`，用法 `python3 <path>/search.py "<query>" --design-system -f markdown [--density 1-10]`，stdout 輸出以 `## Design System:` 開頭的 markdown。後續 task 的 install.sh 與 agent 定義都依賴此路徑結構（`scripts/` + `data/` 同層，core.py 以 `Path(__file__).parent.parent / "data"` 定位資料）。

- [ ] **Step 1: 取得 upstream commit SHA 並下載檔案**

```bash
cd ~/Desktop/dev-factory
SHA=$(git ls-remote https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git HEAD | cut -f1)
echo "$SHA"
mkdir -p vendor/ui-ux-pro-max/scripts vendor/ui-ux-pro-max/data
BASE="https://raw.githubusercontent.com/nextlevelbuilder/ui-ux-pro-max-skill/$SHA"
curl -sfL "$BASE/LICENSE" -o vendor/ui-ux-pro-max/LICENSE
for f in core.py design_system.py search.py; do
  curl -sfL "$BASE/src/ui-ux-pro-max/scripts/$f" -o "vendor/ui-ux-pro-max/scripts/$f"
done
for f in app-interface charts colors google-fonts icons landing motion products react-performance styles typography ui-reasoning ux-guidelines; do
  curl -sfL "$BASE/src/ui-ux-pro-max/data/$f.csv" -o "vendor/ui-ux-pro-max/data/$f.csv"
done
ls vendor/ui-ux-pro-max/scripts vendor/ui-ux-pro-max/data | wc -l   # 期望 3 + 13 + 2 行目錄標頭 → 檢查實際列表
```

Expected: 每個 curl 皆成功（-f 失敗會非零退出）；`scripts/` 3 檔、`data/` 13 檔、LICENSE 存在且開頭為 `MIT License`。

- [ ] **Step 2: 寫 vendor README（含 SHA 與同步方式）**

寫入 `vendor/ui-ux-pro-max/README.md`（`<SHA>`、`<日期>` 代入 Step 1 的實際值與今天日期）：

```markdown
# vendored: ui-ux-pro-max-skill（部分）

- 來源：https://github.com/nextlevelbuilder/ui-ux-pro-max-skill（MIT，LICENSE 見同層）
- 抓取日期：<日期>；upstream commit：`<SHA>`
- 內容：`src/ui-ux-pro-max/scripts/` 的 3 支純標準庫 Python 腳本 + `data/` 的 13 個 domain CSV。
- **未收錄**：`data/stacks/*.csv`（per-stack 實作技巧，S0 生成用不到）、上游 templates 與 tests。
- **腳本一律原樣 vendor、不本地修改**——要改行為就到上游改或換版本。
- 手動同步：重跑 dev-factory repo 的
  `docs/superpowers/plans/2026-07-17-uipro-preset-generator.md` Task 1 Step 1 的指令，
  再把本檔的日期與 SHA 更新即可。
- 用途：install.sh 把本目錄鋪到目標專案 `.claude/uipro/`，`/sprint` 的 S0 設置棒
  跑 `python3 .claude/uipro/scripts/search.py "<query>" --design-system -f markdown`
  依產品類型生成量身 design-system.md。
```

- [ ] **Step 3: 離線驗證生成可跑**

```bash
python3 vendor/ui-ux-pro-max/scripts/search.py "fintech stock dashboard data-dense" --design-system -f markdown | head -15
```

Expected: 首行 `## Design System: FINTECH STOCK DASHBOARD DATA-DENSE`，含 `### Pattern`、`### Style` 段。無網路呼叫、無非零退出。

- [ ] **Step 4: Commit**

```bash
git add vendor/
git commit -m "vendor: ui-ux-pro-max 資料庫與生成腳本（scripts×3 + domain CSV×13，MIT）

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: install.sh 鋪 vendor 到目標專案

**Files:**
- Modify: `install.sh`（`seed_project()`，現於 design-system.md 那行之後、adr-template cp 之前插入）

**Interfaces:**
- Consumes: Task 1 的 `vendor/ui-ux-pro-max/` 目錄結構。
- Produces: 目標專案的 `.claude/uipro/{scripts,data,LICENSE,README.md}`——Task 4/5 的 agent 定義引用的固定路徑 `.claude/uipro/scripts/search.py`。

- [ ] **Step 1: 修改 seed_project()**

在 `install.sh` 中，於這行之後：

```bash
  [ -f "$proj/docs/design/design-system.md" ] || cp "$FACTORY_DIR/templates/design-system.md" "$proj/docs/design/design-system.md"
```

插入：

```bash
  # ui-ux-pro-max vendor（S0 量身 preset 產生器的資料與腳本）：框架資料檔，
  # 使用者不會改，無條件整包更新（與上面 design-system.md 的保護策略不同，是刻意的）
  mkdir -p "$proj/.claude"
  rm -rf "$proj/.claude/uipro"
  cp -R "$FACTORY_DIR/vendor/ui-ux-pro-max" "$proj/.claude/uipro"
```

並把 seed 完成的 echo 行

```bash
  echo "  ✓ docs/ 骨架（PROJECT_GOAL、backlog、DIRECTION、discovery/rubric、design-system、範本）"
```

改為：

```bash
  echo "  ✓ docs/ 骨架（PROJECT_GOAL、backlog、DIRECTION、discovery/rubric、design-system、範本）"
  echo "  ✓ .claude/uipro/（ui-ux-pro-max 資料 + 生成腳本，UX 強度=full 首跑時 S0 量身 preset 用）"
```

- [ ] **Step 2: 煙霧測試——全新安裝**

```bash
SANDBOX="/private/tmp/claude-501/-Users-haosun-Desktop-dev-factory/9ac558c0-0ee7-48db-bddc-013d6a9e8179/scratchpad/install-test"
rm -rf "$SANDBOX" && mkdir -p "$SANDBOX"
~/Desktop/dev-factory/install.sh "$SANDBOX"
ls "$SANDBOX/.claude/uipro/scripts" "$SANDBOX/.claude/uipro/data" | wc -l
cd "$SANDBOX" && python3 .claude/uipro/scripts/search.py "recipe community warm" --design-system -f markdown | head -5
```

Expected: install 輸出含兩行 ✓（docs 骨架、.claude/uipro/）；uipro 檔數齊全（3 腳本 + 13 CSV）；以**專案相對路徑**執行生成成功、首行 `## Design System: RECIPE COMMUNITY WARM`。

- [ ] **Step 3: 煙霧測試——重跑保護**

```bash
echo "CUSTOMIZED" >> "$SANDBOX/docs/design/design-system.md"
~/Desktop/dev-factory/install.sh "$SANDBOX"
tail -1 "$SANDBOX/docs/design/design-system.md"
ls "$SANDBOX/.claude/uipro/data/styles.csv"
```

Expected: 重跑後 design-system.md 末行仍是 `CUSTOMIZED`（保護未破壞）；`.claude/uipro/` 仍齊全（被無條件重鋪）。

- [ ] **Step 4: Commit**

```bash
cd ~/Desktop/dev-factory
git add install.sh
git commit -m "feat(install): seed 時鋪 ui-ux-pro-max vendor 到專案 .claude/uipro/

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: 出廠模板——marker + anti-slop 禁用規則 11–14

**Files:**
- Modify: `templates/design-system.md`

**Interfaces:**
- Produces: 首行 marker `<!-- dev-factory-default-preset -->`（Task 5 的 S0 觸發偵測依賴它）；禁用規則 11–14 的條文與「換 preset 必須保留」註記（Task 4 的 ux-designer S0 翻譯規格引用「出廠模板規則 11–14」這個稱呼）。

- [ ] **Step 1: 首行加 marker**

把檔案開頭

```markdown
# 設計系統（Design System）
```

改為

```markdown
<!-- dev-factory-default-preset -->
# 設計系統（Design System）
```

- [ ] **Step 2: 追加禁用規則 11–14 與保留註記**

在最後一條規則

```markdown
10. **不要擠。** 區塊間距低於 `--space-7` 通常是錯的——慷慨留白是這套 preset 的識別特徵。
```

之後追加：

```markdown
11. **emoji 不得當結構性圖示**（導覽、按鈕、狀態指示、清單項目符號）。用同一家族的 SVG 圖示（lucide / heroicons / phosphor 擇一）；同一層級不得混用 filled 與 outline，筆畫粗細須一致。
12. **hover / pressed 態不得造成版面位移。** 回饋用 color / opacity / shadow / transform 表達，不得改變元素的 layout bounds（hover 時改 border 寬、字重、尺寸都是錯的）。
13. **未經 PROJECT_GOAL 定調，不得使用「AI 紫粉漸層」類配色。** 紫→粉大面積漸層是 generic AI 產出的廉價感標誌；漸層只能由本檔 token 表的色彩構成。
14. **可點擊元素必有 `cursor: pointer` 與 hover 回饋。** 看起來能點但毫無反應的元素是錯的。

> 規則 11–14 是**通用 anti-slop 條款**，與 preset 風格無關：整份換 preset 或由 S0 生成量身版本時，這四條必須原樣保留。
```

- [ ] **Step 3: 驗證定位契約完整**

```bash
head -1 templates/design-system.md
grep -c "^## " templates/design-system.md
grep -n "anti-slop" templates/design-system.md
```

Expected: 首行是 marker；`## ` 計數 3（Design Tokens / 元件 / 禁用規則）；anti-slop 註記存在。

- [ ] **Step 4: Commit**

```bash
git add templates/design-system.md
git commit -m "feat(design-system): 出廠 marker + anti-slop 禁用規則 11-14

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: agent 定義——ux-designer 的 S0 章節 + visual-reviewer 圖示檢查

**Files:**
- Modify: `agents/ux-designer.md`
- Modify: `agents/visual-reviewer.md`

**Interfaces:**
- Consumes: Task 1 的腳本路徑 `.claude/uipro/scripts/search.py`；Task 3 的 marker 與規則 11–14。
- Produces: ux-designer 的「S0 設置棒」章節（Task 5 的 sprint SKILL 派工 prompt 以「S0：生成 design system preset」字樣觸發它）。

- [ ] **Step 1: ux-designer 工具列補 Bash**

`agents/ux-designer.md` frontmatter 的

```yaml
tools: Read, Write, Edit, Glob
```

改為

```yaml
tools: Read, Write, Edit, Glob, Bash
```

並把 frontmatter 的 `description:` 行末尾補上一句 `另可被派一次性 S0 設置棒：生成量身 design-system.md。`（接在原句號後）。

- [ ] **Step 2: ux-designer 加 S0 章節**

在「## 若這是非 UI 專案（後端/CLI/資料）」段**之前**插入：

```markdown
## S0 設置棒：生成量身 design-system.md（僅被明確派此任務時）

派工 prompt 標明「**S0：生成 design system preset**」時，本棒**不寫 sprint UX 規格**，改做以下事（每專案至多一次）：

1. 讀 `docs/PROJECT_GOAL.md`，組一組**英文**查詢關鍵字：產品類型 + 產業 + 風格/密度詞（例 `"fintech stock dashboard data-dense"`、`"recipe sharing community warm friendly"`）。
2. 用 Bash 跑生成腳本（純標準庫、離線）：
   `python3 .claude/uipro/scripts/search.py "<query>" --design-system -f markdown`
   資料密集後台/儀表板類加 `--density 8`；行銷頁/內容站類加 `--density 3`。結果不合適可換關鍵字重跑（上限 3 次，取最合適的一份）。
3. 把輸出**翻譯**成 `docs/design/design-system.md`（覆寫），格式鐵則：
   - 三個 section 標題不變：`## Design Tokens` / `## 元件` / `## 禁用規則`——agent 靠它們定位。
   - **Design Tokens**：色彩表換成生成的色票（保留「Token / 值 / 用途」三欄的表格形式）；間距/字級/圓角/陰影依生成風格調整，但仍必須是離散 scale（不得開放任意值）。
   - **元件**：沿用出廠模板的骨架（按鈕/輸入框/卡片/表格/對話框/狀態呈現），依新 token 與風格改寫描述。
   - **禁用規則**：出廠模板的**通用 anti-slop 條款（規則 11–14）原樣保留**；生成輸出的 Avoid/反模式段翻成該產品類型的禁用條目附加在後。
   - **移除首行的 `<!-- dev-factory-default-preset -->` marker**——表示已量身，之後任何 sprint 都不再重生成。
4. 回報 orchestrator：選了什麼風格/色系/字體、用了什麼查詢與 density、有什麼未盡處（供收尾摘要轉告使用者）。
5. **降級**：`python3` 不存在、腳本失敗、或 `.claude/uipro/` 缺失 → 回報 `SKIPPED: <原因>`，**不動** design-system.md（沿用出廠預設，＝現行行為），不擋 sprint。
```

- [ ] **Step 3: visual-reviewer 讀圖清單補圖示一致性**

`agents/visual-reviewer.md` 的讀圖批判清單，在

```markdown
7. **對照 UX 規格**：實作出來的跟 `sprint-<N>-ux.md` 說的一致嗎？規格說有的狀態，做出來了嗎？
```

之後追加：

```markdown
8. **圖示一致性**（對應禁用規則 11）：有沒有 emoji 被當結構性圖示？圖示是否同一家族、同筆畫粗細？同一層級有沒有混用 filled/outline？截圖看不清就放大截該區塊再讀。
```

- [ ] **Step 4: 驗證與 Commit**

```bash
grep -n "Bash" agents/ux-designer.md | head -2
grep -n "S0" agents/ux-designer.md | head -3
grep -n "圖示一致性" agents/visual-reviewer.md
git add agents/ux-designer.md agents/visual-reviewer.md
git commit -m "feat(agents): ux-designer 增 S0 preset 生成棒（+Bash）；visual-reviewer 增圖示一致性檢查

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: 編排接線——sprint SKILL 的 S0 觸發 + CLAUDE.md 模板

**Files:**
- Modify: `skills/sprint/SKILL.md`（就緒判定第 3 步「UX 強度判定」內）
- Modify: `templates/CLAUDE.md`（「UX 強度」段的 full bullet）

**Interfaces:**
- Consumes: Task 3 的 marker、Task 4 的 S0 章節與「S0：生成 design system preset」觸發字樣。

- [ ] **Step 1: sprint SKILL 插入 S0 觸發**

`skills/sprint/SKILL.md` 就緒判定第 3 步（UX 強度判定）中，在這個 bullet 之後：

```markdown
   - 若選 `full`，順帶確認 PROJECT_GOAL 的「技術約束 → 預覽指令」有填；沒填就一起問（visual-reviewer 靠它起專案；缺了視覺關只能回 SKIPPED）。
```

插入：

```markdown
   - **S0 量身 preset（UX 強度=`full` 時檢查；每專案至多一次）**：讀 `docs/design/design-system.md` **首行**是否為 `<!-- dev-factory-default-preset -->`。
     - **有 marker**（還是出廠 Stripe 預設）→ 本輪 **S1 之前**先派一棒 S0：`subagent_type: ux-designer`，prompt 標明「**S0：生成 design system preset**」（做法在 ux-designer 定義的 S0 章節），並附 `docs/PROJECT_GOAL.md` 要點。完成後把它選的風格記下（收尾摘要轉告使用者），照常進 S1。回 `SKIPPED: <原因>` → 沿用出廠預設照常進 S1，原因記進收尾摘要。**S0 不設修復迴圈**——失敗就降級，不重派。
     - **無 marker**（使用者已客製、或先前已生成）→ 跳過 S0，照舊。
```

- [ ] **Step 2: CLAUDE.md 模板補一句**

`templates/CLAUDE.md` 的 UX 強度段中，找到 full bullet 結尾（`……這是「沒有設計師也能有品味」的機制：品味 = 約束 + 回饋。`），在該句之後（同一 bullet 內）補：

```markdown
首次以 full 開跑且 design-system.md 仍是出廠預設（首行有 marker）時，會先插一棒 S0：ux-designer 用內建的 ui-ux-pro-max 資料庫（`.claude/uipro/`）依產品類型生成量身 preset，之後才進正常管線。
```

- [ ] **Step 3: 驗證與 Commit**

```bash
grep -n "dev-factory-default-preset" skills/sprint/SKILL.md templates/CLAUDE.md templates/design-system.md
git add skills/sprint/SKILL.md templates/CLAUDE.md
git commit -m "feat(sprint): UX 強度=full 首跑時觸發 S0 量身 preset 設置棒

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: 三個檔各至少一處 marker 字串（design-system.md 是定義處、另兩處是偵測/說明）。

---

### Task 6: README 註記——vendor 來源 + 既有專案遷移

**Files:**
- Modify: `README.zh-TW.md`（「## 內容」「## 客製」「## 致謝」三處）
- Modify: `README.md`（對應英文段落）

**Interfaces:**
- Consumes: Task 1–5 的全部產出（對外文件化）。

- [ ] **Step 1: README.zh-TW.md 三處追加**

「## 內容」區塊清單末尾追加：

```markdown
- `vendor/ui-ux-pro-max/` — vendored 設計資料庫與生成腳本（MIT，來源見該目錄 README）；install 時鋪到專案 `.claude/uipro/`，UX 強度=full 首跑的 S0 棒用它依產品類型生成量身 design-system.md。
```

「## 客製」區塊末尾追加：

```markdown
### 既有專案升級到量身 preset

install.sh 不會覆蓋你專案裡的 `docs/design/design-system.md`。舊專案要吃到新東西有兩條路：

1. **只要 anti-slop 規則**：把 `templates/design-system.md` 禁用規則 11–14（emoji 圖示、hover 位移、AI 紫粉漸層、cursor: pointer）手動貼進你專案的 design-system.md。
2. **要量身 preset**：把你專案的 design-system.md 重置為出廠模板（含首行 `<!-- dev-factory-default-preset -->` marker），下次以 UX 強度=full 開跑時 S0 會依 PROJECT_GOAL 重新生成。
```

「## 致謝」區塊追加：

```markdown
- [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)（MIT）——S0 量身 preset 的設計資料庫與生成腳本來源。
```

- [ ] **Step 2: README.md 對應英文追加**

Contents / Customization / Acknowledgements（或對應標題）各追加：

```markdown
- `vendor/ui-ux-pro-max/` — vendored design database + generator scripts (MIT, see that folder's README); seeded into each project's `.claude/uipro/`, used by the one-time S0 step to generate a product-tailored design-system.md on the first full-intensity sprint.
```

```markdown
### Upgrading existing projects to a tailored preset

install.sh never overwrites an existing `docs/design/design-system.md`. Two upgrade paths:

1. **Anti-slop rules only**: manually copy rules 11–14 from `templates/design-system.md` into your project's design-system.md.
2. **Tailored preset**: reset your project's design-system.md to the factory template (with the first-line `<!-- dev-factory-default-preset -->` marker); the next full-intensity sprint's S0 step regenerates it from PROJECT_GOAL.
```

```markdown
- [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (MIT) — source of the design database and generator scripts behind the S0 tailored-preset step.
```

（若 README.md 標題結構與中文版不同，就近放語意對應的區塊；沒有對應區塊就在文件尾新增。）

- [ ] **Step 3: Commit**

```bash
git add README.zh-TW.md README.md
git commit -m "docs: vendor 來源註記與既有專案遷移路徑

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 7: 端到端驗證

**Files:** 無新改動（純驗證；發現問題就修在對應檔案並補 commit）。

- [ ] **Step 1: 全新安裝端到端**

```bash
SANDBOX="/private/tmp/claude-501/-Users-haosun-Desktop-dev-factory/9ac558c0-0ee7-48db-bddc-013d6a9e8179/scratchpad/e2e-test"
rm -rf "$SANDBOX" && mkdir -p "$SANDBOX"
~/Desktop/dev-factory/install.sh "$SANDBOX"
head -1 "$SANDBOX/docs/design/design-system.md"          # 期望：marker
grep -c "^## " "$SANDBOX/docs/design/design-system.md"    # 期望：3
grep -n "anti-slop" "$SANDBOX/docs/design/design-system.md"
cd "$SANDBOX" && python3 .claude/uipro/scripts/search.py "b2b saas admin dashboard" --design-system -f markdown --density 8 | head -20
```

Expected: marker 在首行、三段標題齊、anti-slop 註記在、生成腳本以專案相對路徑可跑且輸出 `## Design System:` 開頭。

- [ ] **Step 2: 契約一致性掃描**

```bash
cd ~/Desktop/dev-factory
grep -rn "dev-factory-default-preset" --include="*.md" --include="*.sh" . | grep -v docs/superpowers | grep -v scratchpad
grep -n "S0：生成 design system preset" agents/ux-designer.md skills/sprint/SKILL.md
grep -n ".claude/uipro" agents/ux-designer.md skills/sprint/SKILL.md templates/CLAUDE.md install.sh README.zh-TW.md
```

Expected: marker 出現在 templates/design-system.md、skills/sprint/SKILL.md、templates/CLAUDE.md、README×2；S0 觸發字樣在 ux-designer 與 sprint SKILL 完全一致；`.claude/uipro` 路徑各處拼寫一致。

- [ ] **Step 3: 收尾**

清掉 sandbox（`rm -rf` 兩個測試目錄）。向使用者回報：改了什麼、驗了什麼、S0 全流程留待下次真實專案首次 full sprint 煙霧測試（同 B-048 模式）。
