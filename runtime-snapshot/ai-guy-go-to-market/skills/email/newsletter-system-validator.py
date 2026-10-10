#!/usr/bin/env python3
"""Validate newsletter Hermes bridge skills against the Obsidian source files."""
from pathlib import Path
import re
import sys

SKILLS_DIR = Path(__file__).parent
VAULT = Path("/opt/data/obsidian-vault/Newsletters")
BRIDGES = {
    "newsletter-system-issue-production": "Issue Production Skill.md",
    "newsletter-system-brand-onboarding": "Brand Onboarding Skill.md",
    "newsletter-system-research": "Research and Sourcing Skill.md",
    "newsletter-system-image-production": "Image Production Skill.md",
    "newsletter-system-qa": "QA Gate Skill.md",
    "newsletter-system-change-control": "Change Control Skill.md",
}


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []
    source_dir = VAULT / "00 - Newsletter System" / "skills"
    for name, source_name in BRIDGES.items():
        path = SKILLS_DIR / name / "SKILL.md"
        if not path.is_file():
            fail(f"missing bridge: {path}", errors)
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            fail(f"{name}: frontmatter must start at byte 0", errors)
        if "\n---\n" not in text[4:]:
            fail(f"{name}: missing frontmatter terminator", errors)
        if f"/opt/data/obsidian-vault/Newsletters/00 - Newsletter System/skills/{source_name}" not in text:
            fail(f"{name}: canonical source path is missing or incorrect", errors)
        if not (source_dir / source_name).is_file():
            fail(f"missing canonical source: {source_dir / source_name}", errors)
        if "single source of truth" not in text.lower():
            fail(f"{name}: does not declare the Obsidian source as authoritative", errors)
        if "Never send, schedule, publish, or test-send" not in text:
            fail(f"{name}: missing no-send safety boundary", errors)
        if re.search(r"(?m)^## (Required sequence|How to build|Detailed workflow)", text):
            fail(f"{name}: appears to contain duplicated workflow content", errors)

    if errors:
        print("FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"PASS: {len(BRIDGES)} bridge skills validated")
    print(f"PASS: {len(BRIDGES)} canonical Obsidian sources exist")
    print("PASS: frontmatter, source links, authority declaration, safety boundary, and anti-duplication checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())


