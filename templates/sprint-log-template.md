# Sprint-<N>

- **目標**：<一句話>
- **期間**：<開始 ~ 結束>

## 納入項目（可追溯 backlog）
- B-00X：<標題>

## 驗收標準（PM 定義，QA/drift 依此判定）
- [ ] <Given/When/Then 或可勾選條件>
- [ ] <…>

## Definition of Done
- [ ] 測試通過
- [ ] 無 High 以上資安發現
- [ ] 飄移稽核 ALIGNED
- [ ] 文件/ADR 更新

## 階段計畫（PM 於 S1 宣告，orchestrator 依此裁剪）
- 治理 profile：<lean / standard / max，取自 PROJECT_GOAL>
- 使用者可見面（S2 UX + S4 一致性）：有 / 無 —— 理由：<無使用者可見介面/契約變更 → 略過 UX 且一致性折進架構自檢>
- 本輪資安（S6 驗證關）：合併快掃 / 拆獨立棒＋完整 —— 理由：<碰 auth/金鑰/外部輸入/反序列化才需拆獨立棒>
- 開發/驗證關/收尾/retro 一律執行

## 執行狀態（orchestrator 每完成一階段就更新；斷點續跑與迴圈計數的唯一真理來源）
- 分支：`sprint-<N>`　profile：<lean/standard/max>
- [ ] S1 PM 規劃
- [ ] S2 UX 設計（無可見面 → 跳過）
- [ ] S3 架構（設計+拆解，一棒融合）
- [ ] S4 一致性 gate（lean/無可見面 → 折進 S3 自檢，跳過）— 退回次數：0/2
- [ ] S5 開發
- [ ] S6 驗證關 — 退回次數：0/3
      - profile 形態：lean=reviewer(功能+資安+飄移) / standard=QA+reviewer(資安+飄移) / max=QA+security+drift
- [ ] S7 PM 收尾（瘦身）
- [ ] S8 retro
- 總修復預算（所有 gate 退回合計）：0/6

---

## 收尾摘要（PM 於 S7 填寫）
- **完成**：<做了什麼>
- **未竟**：<沒做完的、退到下個 sprint 的>
- **各 gate 結果**：一致性 / QA / 資安 / 飄移
- **Demo 重點**：<給使用者看的>
- **下個 sprint 建議**：<…>
