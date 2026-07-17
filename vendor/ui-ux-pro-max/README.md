# vendored: ui-ux-pro-max-skill（部分）

- 來源：https://github.com/nextlevelbuilder/ui-ux-pro-max-skill（MIT，LICENSE 見同層）
- 抓取日期：2026-07-17；upstream commit：`f8ac5e1266dba8354ea96e19994d9f4345e7ec31`
- 內容：`src/ui-ux-pro-max/scripts/` 的 3 支純標準庫 Python 腳本 + `data/` 的 13 個 domain CSV。
- **未收錄**：`data/stacks/*.csv`（per-stack 實作技巧，S0 生成用不到）、上游 templates 與 tests。
- **腳本一律原樣 vendor、不本地修改**——要改行為就到上游改或換版本。
- 手動同步：重跑 dev-factory repo 的
  `docs/superpowers/plans/2026-07-17-uipro-preset-generator.md` Task 1 Step 1 的指令，
  再把本檔的日期與 SHA 更新即可。
- 用途：install.sh 把本目錄鋪到目標專案 `.claude/uipro/`，`/sprint` 的 S0 設置棒
  跑 `python3 .claude/uipro/scripts/search.py "<query>" --design-system -f markdown`
  依產品類型生成量身 design-system.md。
