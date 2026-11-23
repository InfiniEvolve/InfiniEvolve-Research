"""Scripted stand-in: checks installation without spending model tokens."""
import json
import os
from pathlib import Path
import sys
import subprocess

prompt = sys.stdin.read()
assert "scripted integration check" in prompt
backend = "codex" if Path(".agents/skills").is_dir() else "claude"
skill_root = Path(".agents/skills" if backend == "codex" else ".claude/skills")
skills = sorted(skill_root.glob("*/SKILL.md"))
assert len(skills) == 87
assert (skill_root / "research-lit/SKILL.md").read_text()
assert (skill_root / "shared-references/integration-contract.md").is_file()
assert Path(".aris/tools/research_wiki.py").is_file()
assert Path(".aris/templates/EXPERIMENT_PLAN_TEMPLATE.md").is_file()
assert Path(os.environ["ARIS_REPO"]).is_dir()
Path("solution.py").write_text("prediction = 2.0\n")
trace = Path(".aris/traces/smoke.json")
trace.parent.mkdir(parents=True, exist_ok=True)
revision = subprocess.check_output(["git", "-C", os.environ["ARIS_REPO"], "rev-parse", "HEAD"], text=True).strip()
trace.write_text(json.dumps({"scripted": True, "backend": backend,
                             "skills_readable": len(skills),
                             "aris_revision": revision}, indent=2) + "\n")
print("SESSION-REPORT-BEGIN\nsummary: Scripted integration check; native skills and helpers readable.\n"
      "evidence: .aris/traces/smoke.json\nSESSION-REPORT-END")
