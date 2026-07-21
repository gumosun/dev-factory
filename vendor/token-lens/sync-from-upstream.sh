#!/usr/bin/env bash
# 從 upstream token-lens repo 同步「執行期」檔到此 vendor 快照。
#
# token-lens 是獨立 repo(完整專案含 22 個測試 / report.html / README 在那裡)。
# 這個 vendor 只放 dev-factory 的 retro / architect 在執行期會呼叫的檔——讓 install 後
# 的專案自足、不依賴 upstream 存在。改請改 upstream,再跑此腳本同步,別在此直接編輯。
#
# 用法: ./sync-from-upstream.sh [upstream_path]   (預設 ~/Desktop/token-lens)
set -euo pipefail
UP="${1:-$HOME/Desktop/token-lens}"
DST="$(cd "$(dirname "$0")" && pwd)"
[ -d "$UP" ] || { echo "找不到 upstream: $UP" >&2; exit 1; }

for f in ledger.py quality.py radar.py apply_policy.py router.py retro_optimize.py \
         router-policy.yaml model-intel.json thresholds.txt; do
  cp "$UP/$f" "$DST/$f"
done
mkdir -p "$DST/seed"
cp "$UP/seed/sprint-sample.json" "$DST/seed/"
echo "✓ 已從 $UP 同步 runtime 檔到 vendor/token-lens/"
