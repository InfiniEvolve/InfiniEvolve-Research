"""Scripted stand-in: checks installation without spending model tokens."""
import json
import os
from pathlib import Path
import sys

prompt = sys.stdin.read()
assert "scripted integration check" in prompt
manifest = next(Path(".aris").glob("infinievolve-skills-*.json"))
installed = json.loads(manifest.read_text())
skill_root = Path(installed["skill_root"])
for name in installed["skills"]:
    assert (skill_root / name / "SKILL.md").is_file(), name
assert "research-lit" in installed["skills"]
assert (skill_root / "research-lit/SKILL.md").read_text()
assert (skill_root / "shared-references/integration-contract.md").is_file()
assert Path(".aris/tools/research_wiki.py").is_file()
assert Path(".aris/templates/EXPERIMENT_PLAN_TEMPLATE.md").is_file()
assert Path(os.environ["ARIS_REPO"]).is_dir()
Path("solution.py").write_text("prediction = 2.0\n")
trace = Path(".aris/traces/smoke.json")
trace.parent.mkdir(parents=True, exist_ok=True)
trace.write_text(json.dumps({"scripted": True, "backend": installed["backend"],
                             "skills_readable": len(installed["skills"]),
                             "aris_revision": installed["revision"]}, indent=2) + "\n")
print("SESSION-REPORT-BEGIN\nsummary: Scripted integration check; native skills and helpers readable.\n"
      "evidence: .aris/traces/smoke.json\nSESSION-REPORT-END")
