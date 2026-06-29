#!/usr/bin/env python3
"""Scan skill directories and print name + description for sub-agent preload."""

import os
import re
import glob as glob_mod
import argparse

SKILL_DIRS = [
    ".agents/skills",
    ".codex/skills",
    ".claude/skills",
]


def parse_frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    front = m.group(1)
    result = {}
    for line in front.strip().split("\n"):
        kv = re.match(r"(\w+):\s*(.*)", line)
        if kv:
            result[kv.group(1)] = kv.group(2).strip().strip('"').strip("'")
    return result


def scan_skills(root):
    skills = []
    for pattern in ["**/SKILL.md", "**/skill.md"]:
        for path in glob_mod.glob(os.path.join(root, pattern), recursive=True):
            with open(path, encoding="utf-8") as f:
                meta = parse_frontmatter(f.read())
            name = meta.get("name", os.path.basename(os.path.dirname(path)))
            desc = meta.get("description", "(no description)")
            skills.append((name, desc, path))
    return skills


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--format", choices=["list", "json"], default="list")
    parser.add_argument("--no-path", action="store_true")
    args = parser.parse_args()

    root = os.path.abspath(args.project_root)
    all_skills = []
    seen = set()
    for d in SKILL_DIRS:
        full = os.path.join(root, d)
        if os.path.isdir(full):
            for name, desc, path in scan_skills(full):
                if name not in seen:
                    seen.add(name)
                    all_skills.append((name, desc, path))

    all_skills.sort(key=lambda x: x[0])

    if args.format == "json":
        import json
        data = [{"name": n, "description": d} for n, d, _ in all_skills]
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        for name, desc, path in all_skills:
            if args.no_path:
                print(f"[{name}]  {desc}")
            else:
                print(f"[{name}]  {desc}  ({path})")

    print(f"\n--- {len(all_skills)} skills found ---")


if __name__ == "__main__":
    main()
