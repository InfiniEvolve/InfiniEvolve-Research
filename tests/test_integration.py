from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

import pytest

from infinievolve_research.cli import main
from infinievolve_research.runtime import aris_repository, install_skills


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("backend", ["codex", "claude"])
def test_real_scheduler_round_trip(tmp_path, backend):
    """Real upstream scheduler, fresh processes and evaluator; only the model is scripted."""
    task = tmp_path / "task"
    shutil.copytree(ROOT / "examples/smoke", task, ignore=shutil.ignore_patterns("runs", "__pycache__"))
    command = shlex.join([sys.executable, "-m", "infinievolve_research", "agent", "--backend", backend,
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
        assert "diff --git a/.aris/infinievolve-skills" not in patch
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
    repo = aris_repository()
    conflict = tmp_path / ".agents/skills/research-lit"
    conflict.mkdir(parents=True)
    (conflict / "SKILL.md").write_text("user-owned skill")
    with pytest.raises(ValueError, match="refusing to replace"):
        install_skills(tmp_path, "codex", repo)
    assert (conflict / "SKILL.md").read_text() == "user-owned skill"
    assert not (tmp_path / ".aris").exists()
    shutil.rmtree(conflict)
    first = install_skills(tmp_path, "codex", repo)
    second = install_skills(tmp_path, "codex", repo)
    assert first == second
    assert len(first["skills"]) == 87


def test_custom_command_preserves_stdin_environment_and_exit_code(tmp_path):
    snippet = "import os,sys; print(os.environ['EVOLVE_TASK']); print(sys.stdin.read()); sys.exit(23)"
    command = [sys.executable, "-m", "infinievolve_research", "agent", "--backend", "codex",
               "--", sys.executable, "-c", snippet]
    result = subprocess.run(command, cwd=tmp_path, input="the original prompt", capture_output=True,
                            text=True, env={**os.environ, "EVOLVE_TASK": "unchanged-task"})
    assert result.returncode == 23, result.stderr
    assert result.stdout == "unchanged-task\nthe original prompt\n"


@pytest.mark.parametrize("spec", ["codex/example-model:xhigh", "claude/example-model:high"])
def test_named_agent_reuses_upstream_command(monkeypatch, spec):
    from infinievolve.local import agent_command
    seen = []
    monkeypatch.setattr("infinievolve_research.cli.launch", lambda *args: seen.append(args))
    assert main(["agent", "--agent", spec]) == 0
    assert seen[0][0] == spec.split("/", 1)[0]
    assert seen[0][1] == agent_command(spec)[0]
