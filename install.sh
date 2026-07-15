#!/usr/bin/env bash
# dev-factory installer — 把這套多角色自主開發機制裝進一個目標專案。
#
# 用法：
#   在「目標專案根目錄」執行：
#     /path/to/dev-factory/install.sh                      # 裝進當前資料夾（專案層級，預設）
#     /path/to/dev-factory/install.sh /path/to/project
#     /path/to/dev-factory/install.sh --user               # 裝到 ~/.claude（所有專案共用 agents/skills）
#     /path/to/dev-factory/install.sh --seed-only [path]   # 只鋪 CLAUDE.md + docs/ 骨架（搭配 --user 使用）
#     /path/to/dev-factory/install.sh --force [path]       # 連你本地改過的 agents/skills 也覆蓋
#
# 升級保護：安裝時把每個檔案的 hash 記進 <claude_dir>/.dev-factory-manifest。
# 重跑 install 時，凡本地被改過的檔案（例如已核可的 PROJECT-local agent 客製）一律跳過並警告，
# 除非加 --force。
set -euo pipefail

FACTORY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

MODE="project"
FORCE=0
TARGET="$(pwd)"
for arg in "$@"; do
  case "$arg" in
    --user)      MODE="user" ;;
    --seed-only) MODE="seed" ;;
    --force)     FORCE=1 ;;
    -*)          echo "未知選項：$arg"; exit 1 ;;
    *)           TARGET="$arg" ;;
  esac
done

hash_of() { shasum -a 256 "$1" | awk '{print $1}'; }

# 帶升級保護地複製 agents/ 與 skills/ 到 <claude_dir>
copy_core() {
  local claude_dir="$1"
  local manifest="$claude_dir/.dev-factory-manifest"
  local new_manifest
  new_manifest="$(mktemp)"
  mkdir -p "$claude_dir/agents" "$claude_dir/skills"

  local src rel dst cur recorded skip
  for src in "$FACTORY_DIR"/agents/*.md "$FACTORY_DIR"/skills/*/SKILL.md; do
    rel="${src#"$FACTORY_DIR"/}"
    dst="$claude_dir/$rel"
    mkdir -p "$(dirname "$dst")"
    skip=0
    recorded=""
    if [ -f "$dst" ] && [ "$FORCE" -ne 1 ]; then
      cur="$(hash_of "$dst")"
      if [ -f "$manifest" ]; then
        recorded="$(awk -v f="$rel" '$2==f {print $1}' "$manifest")"
      fi
      if [ -n "$recorded" ]; then
        # 上次是我們裝的：內容變了 = 使用者改過 → 保護
        [ "$cur" != "$recorded" ] && skip=1
      else
        # 沒有安裝記錄的既有檔：與新來源不同就保護
        [ "$cur" != "$(hash_of "$src")" ] && skip=1
      fi
    fi
    if [ "$skip" -eq 1 ]; then
      echo "  ! 跳過 ${rel}（偵測到本地修改；確定要覆蓋請加 --force）"
      # 保留舊記錄，下次仍能辨識這是被改過的檔
      [ -n "$recorded" ] && echo "$recorded $rel" >> "$new_manifest"
    else
      cp "$src" "$dst"
      echo "$(hash_of "$dst") $rel" >> "$new_manifest"
    fi
  done
  mv "$new_manifest" "$manifest"
  echo "  ✓ agents → $claude_dir/agents/（建造 10 角含合併驗證關 reviewer + discovery 3 角 explorer/critic/shaper）"
  echo "  ✓ skills → $claude_dir/skills/（/sprint 建造管線、/discovery 前置管線）"
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
           "$proj/docs/design/adr" "$proj/docs/design/review" "$proj/docs/retro" \
           "$proj/docs/discovery"
  [ -f "$proj/docs/PROJECT_GOAL.md" ] || cp "$FACTORY_DIR/templates/PROJECT_GOAL.md" "$proj/docs/PROJECT_GOAL.md"
  [ -f "$proj/docs/backlog.md" ]      || cp "$FACTORY_DIR/templates/backlog.md"      "$proj/docs/backlog.md"
  [ -f "$proj/docs/LESSONS.md" ]      || cp "$FACTORY_DIR/templates/LESSONS.md"      "$proj/docs/LESSONS.md"
  [ -f "$proj/docs/DIRECTION.md" ]    || cp "$FACTORY_DIR/templates/DIRECTION.md"    "$proj/docs/DIRECTION.md"
  [ -f "$proj/docs/discovery/rubric.md" ] || cp "$FACTORY_DIR/templates/discovery-rubric.md" "$proj/docs/discovery/rubric.md"
  cp "$FACTORY_DIR/templates/adr-template.md"        "$proj/docs/design/adr/_TEMPLATE.md"
  cp "$FACTORY_DIR/templates/sprint-log-template.md" "$proj/docs/sprints/_TEMPLATE.md"
  echo "  ✓ docs/ 骨架（PROJECT_GOAL、backlog、DIRECTION、discovery/rubric、範本）"
  # 建議權限 allowlist（減少自主連跑時被權限提示打斷）：不覆蓋既有 settings.json
  if [ ! -f "$proj/.claude/settings.json" ]; then
    mkdir -p "$proj/.claude"
    cat > "$proj/.claude/settings.json" <<'EOF'
{
  "permissions": {
    "allow": [
      "WebSearch",
      "WebFetch(domain:github.com)"
    ]
  }
}
EOF
    echo "  ✓ .claude/settings.json（discovery 用的 WebSearch/WebFetch allowlist）"
    echo "    → 建議再補上你專案的測試/建置指令，例如 \"Bash(npm test:*)\"，自主連跑才不會被權限提示打斷"
  fi
}

case "$MODE" in
  user)
    echo "→ 安裝到使用者層級（~/.claude）"
    copy_core "$HOME/.claude"
    echo ""
    echo "完成。agents 與 /sprint、/discovery 現在所有專案都可用。"
    echo "每個要用這套機制的專案，仍需各自鋪 CLAUDE.md + docs/："
    echo "  $FACTORY_DIR/install.sh --seed-only /path/to/project"
    ;;
  seed)
    echo "→ 只鋪專案骨架：$TARGET"
    seed_project "$TARGET"
    echo ""
    echo "完成。編輯 docs/PROJECT_GOAL.md 與 docs/backlog.md 後即可跑 /sprint。"
    ;;
  project)
    echo "→ 安裝到專案層級：$TARGET"
    copy_core "$TARGET/.claude"
    seed_project "$TARGET"
    echo ""
    echo "完成。接下來："
    echo "  1. 編輯 $TARGET/docs/PROJECT_GOAL.md 填入你的專案目標"
    echo "  2. 在 $TARGET/docs/backlog.md 列幾個待辦"
    echo "  3. 在該專案開 Claude Code，切到 accept-edits 權限模式（Shift+Tab）"
    echo "  4. 開場輸入：讀 CLAUDE.md，依自主 sprint 工作流開始開發，先跑單輪後給我摘要"
    ;;
esac
