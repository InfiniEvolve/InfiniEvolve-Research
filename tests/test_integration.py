from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import importlib.util

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/with_skills.py"
spec = importlib.util.spec_from_file_location("with_skills", SCRIPT)
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)


@pytest.mark.parametrize("backend", ["codex", "claude"])
def test_real_scheduler_round_trip(tmp_path, backend):
    """Real upstream scheduler, fresh processes and evaluator; only the model is scripted."""
    task = tmp_path / "task"
    shutil.copytree(ROOT / "tests/fixtures/smoke", task, ignore=shutil.ignore_patterns("__pycache__"))
    command = shlex.join([sys.executable, str(SCRIPT), backend,
                          "--", sys.executable, str(task / "fake_agent.py")])
    run = subprocess.run([sys.executable, "-m", "infinievolve.cli", "run", str(task), "--sessions", "3",
                          "--agent-command", command], capture_output=True, text=True, timeout=45)
    assert run.returncode == 0, run.stdout + run.stderr
    campaign = task / "runs/default"
    sessions = campaign / "tasks/task/sessions"
    roots = sorted(path for path in sessions.iterdir() if (path / "node.json").exists())
    assert len(roots) >= 3, run.stdout
    for session in roots[1:]:
        trace = json.loads((session / "work/.aris/traces/smoke.json").read_text())
        assert trace["backend"] == backend
        assert trace["skills_readable"] == 87
        assert trace["aris_revision"] == "4ba94ae2a1c1fbbb14858750dd8764cabf6c28bd"
        patch = (session / "raw/final.patch").read_text()
        assert ".aris/traces/smoke.json" in patch
        assert "diff --git a/.agents/" not in patch
        assert "diff --git a/.claude/skills/" not in patch
        assert "diff --git a/.aris/tools" not in patch
        row = json.loads((session / "raw/result.json").read_text())["row"]
        assert row["checks"]["finite_prediction"]
        assert row["metrics"]["mse"] == pytest.approx(2 / 3)
    # The second agent session actually inherits the first candidate's captured work.
    assert (roots[2] / "input/start.patch").is_file()
    assert "prediction = 2.0" in (roots[2] / "input/start.patch").read_text()
    # Reopening a finished campaign reuses it rather than launching another batch.
    resumed = subprocess.run([sys.executable, "-m", "infinievolve.cli", "run", str(task)],
                             capture_output=True, text=True, timeout=15)
    assert resumed.returncode == 0, resumed.stdout + resumed.stderr
    assert len(list(sessions.glob("*/node.json"))) == len(roots)


def test_existing_skill_is_preserved_and_install_is_repeatable(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    conflict = tmp_path / ".agents/skills/research-lit"
    conflict.mkdir(parents=True)
    (conflict / "SKILL.md").write_text("user-owned skill")
    with pytest.raises(ValueError, match="refusing to replace"):
        script.mount_skills(tmp_path, "codex")
    assert (conflict / "SKILL.md").read_text() == "user-owned skill"
    assert not (tmp_path / ".aris").exists()
    shutil.rmtree(conflict)
    script.mount_skills(tmp_path, "codex")
    first = (tmp_path / ".git/info/exclude").read_text()
    script.mount_skills(tmp_path, "codex")
    assert (tmp_path / ".git/info/exclude").read_text() == first
    assert len(list((tmp_path / ".agents/skills").glob("*/SKILL.md"))) == 87


def test_custom_command_preserves_stdin_environment_and_exit_code(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    snippet = "import os,sys; print(os.environ['EVOLVE_TASK']); print(sys.stdin.read()); sys.exit(23)"
    command = [sys.executable, str(SCRIPT), "codex",
               "--", sys.executable, "-c", snippet]
    result = subprocess.run(command, cwd=tmp_path, input="the original prompt", capture_output=True,
                            text=True, env={**os.environ, "EVOLVE_TASK": "unchanged-task"})
    assert result.returncode == 23, result.stderr
    assert result.stdout == "unchanged-task\nthe original prompt\n"


@pytest.mark.parametrize("spec", ["codex/example-model:xhigh", "claude/example-model:high"])
def test_named_agent_reuses_upstream_command(monkeypatch, spec):
    from infinievolve.local import agent_command
    seen = []
    monkeypatch.setattr(script, "mount_skills", lambda *args: None)
    monkeypatch.setattr(script.os, "execvpe", lambda *args: seen.append(args))
    assert script.main([spec]) == 0
    assert seen[0][0] == agent_command(spec)[0][0]
    assert seen[0][1] == agent_command(spec)[0]
