# vendor/token-lens — 這是快照，不是原始碼

這裡是 **token-lens 的 runtime 快照**，被 `install.sh` 鋪進每個專案的 `.claude/token-lens/`，供 `retro` / `architect` 在執行期呼叫。

- **完整專案在獨立 repo**：`~/Desktop/token-lens`（含 22 個單元測試、`report.html` 視覺報告、完整 README 與自我學習迴圈的說明）。
- **不要在這裡改**——改上游，再跑 `./sync-from-upstream.sh` 同步回來。
- 這裡只放執行期需要的檔（ledger / quality / radar / router / retro_optimize / policy / intel / seed），不含測試與展示物，讓安裝後的專案自足。

含自我學習迴圈:`retro_optimize.py` 把每輪 sprint 的成本×品質 → champion/challenger 晉升提案(帕累托 + criticality 硬地板),晉升走人類核可,引擎不自改建議表。
