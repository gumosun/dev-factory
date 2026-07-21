#!/usr/bin/env python3
"""token-lens Router — 把 router-policy.yaml 的 model 指派套用到目標專案的 .claude/agents/*.md。
用法: python3 apply_policy.py /path/to/project [--dry-run]
只改 frontmatter 的 model: 欄位;effort 與兩段式升層屬 orchestrator 層建議,不在此檔強改。
"""
import re
import sys
from pathlib import Path

POLICY = Path(__file__).parent / "router-policy.yaml"

def load_policy():
    """輕量解析(只取 roles.<name>.model,避免 yaml 依賴)"""
    roles, cur = {}, None
    in_roles = False
    for line in POLICY.read_text().splitlines():
        if line.startswith("roles:"):
            in_roles = True
            continue
        if in_roles and line and not line.startswith(" ") :
            in_roles = False
        if not in_roles:
            continue
        m = re.match(r"^  (\w[\w-]*):\s*$", line)
        if m:
            cur = m.group(1)
            continue
        m = re.match(r"^    model:\s*(\w+)", line)
        if m and cur:
            roles[cur] = m.group(1)
            cur_model = m.group(1)
    return roles

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    target = Path(sys.argv[1]) / ".claude" / "agents"
    dry = "--dry-run" in sys.argv
    if not target.is_dir():
        print(f"找不到 {target}")
        sys.exit(1)
    roles = load_policy()
    changed = 0
    for f in sorted(target.glob("*.md")):
        role = f.stem
        if role not in roles:
            continue
        text = f.read_text()
        m = re.search(r"^model:\s*(\S+)\s*$", text, re.M)
        want = roles[role]
        if m:
            have = m.group(1)
            if have == want:
                print(f"  = {role}: {have}(不變)")
                continue
            new_text = re.sub(r"^model:\s*\S+\s*$", f"model: {want}", text, count=1, flags=re.M)
            print(f"  → {role}: {have} → {want}")
        else:
            # 沒有 model 欄位:插入到 frontmatter 第二行
            new_text = re.sub(r"^(---\n)", rf"\1model: {want}\n", text, count=1)
            print(f"  + {role}: (無) → {want}")
        if not dry:
            f.write_text(new_text)
        changed += 1
    print(f"{'[dry-run] ' if dry else ''}共 {changed} 個角色調整。品質驗證:跑一個 sprint,比對 gate 通過率與退回迴圈數。")

if __name__ == "__main__":
    main()
