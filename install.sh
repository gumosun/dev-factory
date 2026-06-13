#!/usr/bin/env bash
# dev-factory installer — 把這套多角色自主開發機制裝進一個目標專案。
#
# 用法：
#   在「目標專案根目錄」執行：
#     /path/to/dev-factory/install.sh            # 裝進當前資料夾（專案層級，預設）
#     /path/to/dev-factory/install.sh /path/to/project
#     /path/to/dev-factory/install.sh --user     # 裝到 ~/.claude（所有專案共用 agents/skill）
#
# 預設「專案層級」：複製進 <project>/.claude/，專案自我完備、可進 git，升級就重跑。
set -euo pipefail

FACTORY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

MODE="project"
TARGET="$(pwd)"
for arg in "$@"; do
  case "$arg" in
    --user) MODE="user" ;;
    -*)     echo "未知選項：$arg"; exit 1 ;;
    *)      TARGET="$arg" ;;
  esac
done

copy_core() {
  local claude_dir="$1"
  mkdir -p "$claude_dir/agents" "$claude_dir/skills"
  cp "$FACTORY_DIR"/agents/*.md "$claude_dir/agents/"
  cp -R "$FACTORY_DIR"/skills/sprint "$claude_dir/skills/"
  echo "  ✓ agents → $claude_dir/agents/"
  echo "  ✓ skill  → $claude_dir/skills/sprint/"
}

seed_project() {
  local proj="$1"
  # CLAUDE.md：存在就不覆蓋，附加提示
  if [ -f "$proj/CLAUDE.md" ]; then
    echo "  ! $proj/CLAUDE.md 已存在 → 跳過，請手動併入 templates/CLAUDE.md 的內容"
  else
    cp "$FACTORY_DIR/templates/CLAUDE.md" "$proj/CLAUDE.md"
    echo "  ✓ CLAUDE.md（orchestrator 契約）"
  fi
  # docs 骨架
  mkdir -p "$proj/docs/sprints" "$proj/docs/design/ux" "$proj/docs/design/tech" \
           "$proj/docs/design/adr" "$proj/docs/design/review" "$proj/docs/retro"
  [ -f "$proj/docs/PROJECT_GOAL.md" ] || cp "$FACTORY_DIR/templates/PROJECT_GOAL.md" "$proj/docs/PROJECT_GOAL.md"
  [ -f "$proj/docs/backlog.md" ]      || cp "$FACTORY_DIR/templates/backlog.md"      "$proj/docs/backlog.md"
  [ -f "$proj/docs/LESSONS.md" ]      || cp "$FACTORY_DIR/templates/LESSONS.md"      "$proj/docs/LESSONS.md"
  cp "$FACTORY_DIR/templates/adr-template.md"        "$proj/docs/design/adr/_TEMPLATE.md"
  cp "$FACTORY_DIR/templates/sprint-log-template.md" "$proj/docs/sprints/_TEMPLATE.md"
  echo "  ✓ docs/ 骨架（PROJECT_GOAL、backlog、範本）"
}

if [ "$MODE" = "user" ]; then
  echo "→ 安裝到使用者層級（~/.claude）"
  copy_core "$HOME/.claude"
  echo ""
  echo "完成。agents 與 /sprint 現在所有專案都可用。"
  echo "每個要用這套機制的專案，仍需各自放 CLAUDE.md + docs/："
  echo "  $FACTORY_DIR/install.sh --seed-only /path/to/project   # 之後可加此模式"
else
  echo "→ 安裝到專案層級：$TARGET"
  copy_core "$TARGET/.claude"
  seed_project "$TARGET"
  echo ""
  echo "完成。接下來："
  echo "  1. 編輯 $TARGET/docs/PROJECT_GOAL.md 填入你的專案目標"
  echo "  2. 在 $TARGET/docs/backlog.md 列幾個待辦"
  echo "  3. 在該專案開 Claude Code，切到 accept-edits 權限模式（Shift+Tab）"
  echo "  4. 開場輸入：讀 CLAUDE.md，依自主 sprint 工作流開始開發，先跑單輪後給我摘要"
fi
