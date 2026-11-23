#!/usr/bin/env python3
"""Mount ARIS skills in the current session, then run the agent unchanged."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


ARIS = Path(__file__).resolve().parents[1] / "skills/aris"
BACKENDS = {"claude": ".claude/skills", "codex": ".agents/skills"}


def git(workspace: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(workspace), *args], text=True).strip()


def mount_skills(workspace: Path, backend: str) -> None:
    source = ARIS / ("skills/skills-codex" if backend == "codex" else "skills")
    skills = sorted(source.glob("*/SKILL.md"))
    if not skills:
        raise ValueError("ARIS skills missing; run git submodule update --init --recursive")
    mounts = {Path(BACKENDS[backend]) / skill.parent.name: skill.parent for skill in skills}
    mounts[Path(BACKENDS[backend]) / "shared-references"] = source / "shared-references"
    mounts[Path(".aris/tools")] = ARIS / "tools"
    mounts[Path(".aris/templates")] = ARIS / "templates"
    if backend == "claude":
        mounts[Path(".claude/agents/aris-fanout-leaf.md")] = ARIS / "agents/aris-fanout-leaf.md"

    # Validate all destinations first. Never overwrite an existing user skill or global config.
    for relative, target in mounts.items():
        destination = workspace / relative
        if not target.exists():
            raise ValueError(f"ARIS dependency missing: {target}")
        for parent in destination.parents:
            if parent == workspace:
                break
            if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
                raise ValueError(f"skill parent is not a local directory: {parent}")
        if destination.is_symlink() and destination.resolve() == target.resolve():
            continue
        if destination.exists() or destination.is_symlink():
            raise ValueError(f"refusing to replace existing skill/helper: {destination}")

    # InfiniEvolve captures this repository as a patch. Exclude only the mounted dependencies;
    # research outputs such as .aris/traces must still be archived and inherited.
    if Path(git(workspace, "rev-parse", "--show-toplevel")).resolve() != workspace:
        raise ValueError("run in the InfiniEvolve session repository root")
    if git(workspace, "ls-files", "--", *map(str, mounts)):
        raise ValueError("skill paths are tracked; mount after the session copy is created")
    exclude = Path(git(workspace, "rev-parse", "--git-path", "info/exclude"))
    if not exclude.is_absolute():
        exclude = workspace / exclude
    existing = exclude.read_text().splitlines() if exclude.exists() else []
    missing = ["/" + path.as_posix() for path in mounts if "/" + path.as_posix() not in existing]
    if missing:
        exclude.parent.mkdir(parents=True, exist_ok=True)
        with exclude.open("a") as stream:
            stream.write("\n# ARIS skill mounts\n" + "\n".join(missing) + "\n")
    for relative, target in mounts.items():
        destination = workspace / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.is_symlink():
            destination.symlink_to(target, target_is_directory=target.is_dir())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("agent", help="codex/MODEL[:EFFORT] or claude/MODEL[:EFFORT]; "
                        "for a custom command: codex|claude -- COMMAND ...")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    try:
        backend = args.agent.split("/", 1)[0]
        if backend not in BACKENDS:
            raise ValueError("agent must use codex or claude")
        command = args.command[1:] if args.command[:1] == ["--"] else args.command
        if command:
            if args.agent != backend:
                raise ValueError("use just codex or claude before a custom command")
        else:
            from infinievolve.local import agent_command
            command, _ = agent_command(args.agent)
        mount_skills(Path.cwd().resolve(), backend)
        os.execvpe(command[0], command, {**os.environ, "ARIS_REPO": str(ARIS)})
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"with_skills: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
