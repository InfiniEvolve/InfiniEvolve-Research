"""Mount an unmodified ARIS skill pack before the existing agent starts."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess


BACKENDS = {"claude": ".claude/skills", "codex": ".agents/skills"}


def aris_repository(explicit: str | None = None) -> Path:
    configured = explicit or os.environ.get("INFINIEVOLVE_RESEARCH_ARIS")
    root = Path(configured).expanduser() if configured else Path(__file__).resolve().parents[2] / "vendor/aris"
    root = root.resolve()
    if not (root / "skills/research-lit/SKILL.md").is_file():
        raise ValueError(f"ARIS checkout not found at {root}; run git submodule update --init --recursive "
                         "or set --aris-repo")
    return root


def _git(workspace: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(workspace), *args], capture_output=True, text=True)


def install_skills(workspace: Path, backend: str, repository: Path) -> dict:
    """Only mount skills and their helpers; never run an upstream installer or change user globals.

    This runs AFTER InfiniEvolve prepares a session's Git copy. Exact mounted paths are excluded
    from its patch capture. Research output, including .aris/traces, remains part of that patch.
    """
    if backend not in BACKENDS:
        raise ValueError(f"unknown backend: {backend}")
    workspace, repository = workspace.resolve(), repository.resolve()
    if not workspace.is_dir():
        raise ValueError(f"workspace does not exist: {workspace}")
    source = repository / ("skills/skills-codex" if backend == "codex" else "skills")
    skills = sorted(path for path in source.iterdir() if path.is_dir() and (path / "SKILL.md").is_file())
    if not skills:
        raise ValueError(f"no skills found in {source}")
    mounts = {Path(BACKENDS[backend]) / path.name: path for path in skills}
    mounts[Path(BACKENDS[backend]) / "shared-references"] = source / "shared-references"
    mounts[Path(".aris/tools")] = repository / "tools"
    mounts[Path(".aris/templates")] = repository / "templates"
    if backend == "claude":
        mounts[Path(".claude/agents/aris-fanout-leaf.md")] = repository / "agents/aris-fanout-leaf.md"
    manifest_path = Path(f".aris/infinievolve-skills-{backend}.json")

    # Refuse conflicts before writing any links. A mounted pack is a dependency, not an edit to
    # a user's existing skill. The same installation is safe to run again.
    for relative, target in mounts.items():
        destination = workspace / relative
        if not target.exists():
            raise ValueError(f"ARIS dependency missing: {target}")
        for parent in destination.parents:
            if parent == workspace:
                break
            if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
                raise ValueError(f"skill destination parent is not a local directory: {parent}")
        if destination.is_symlink() and destination.resolve() == target.resolve():
            continue
        if destination.exists() or destination.is_symlink():
            raise ValueError(f"refusing to replace existing skill/helper: {destination}")

    # Native installation should not become part of the candidate diff. Do not exclude the whole
    # .aris directory: reviewer traces and research state are outputs that must survive sessions.
    git_root = _git(workspace, "rev-parse", "--show-toplevel")
    if git_root.returncode == 0:
        if Path(git_root.stdout.strip()).resolve() != workspace:
            raise ValueError("install inside the session repository root, not a nested directory")
        ignored = [*mounts, manifest_path]
        tracked = _git(workspace, "ls-files", "--", *[str(path) for path in ignored])
        if tracked.returncode or tracked.stdout.strip():
            raise ValueError("skill installation paths are already tracked; install after the session copy is created")
        result = _git(workspace, "rev-parse", "--git-path", "info/exclude")
        if result.returncode:
            raise ValueError(result.stderr.strip())
        exclude = Path(result.stdout.strip())
        if not exclude.is_absolute():
            exclude = workspace / exclude
        existing = exclude.read_text() if exclude.exists() else ""
        patterns = ["/" + path.as_posix() for path in ignored]
        missing = [pattern for pattern in patterns if pattern not in existing.splitlines()]
        if missing:
            exclude.parent.mkdir(parents=True, exist_ok=True)
            with exclude.open("a") as stream:
                stream.write("\n# InfiniEvolve-Research runtime dependencies\n" + "\n".join(missing) + "\n")

    for relative, target in mounts.items():
        destination = workspace / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.is_symlink():
            destination.symlink_to(target, target_is_directory=target.is_dir())

    revision = _git(repository, "rev-parse", "HEAD")
    manifest = {"backend": backend, "repository": str(repository),
                "revision": revision.stdout.strip() if revision.returncode == 0 else None,
                "skills": [path.name for path in skills], "skill_root": str(workspace / BACKENDS[backend])}
    (workspace / manifest_path).write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def launch(backend: str, command: list[str], repository: Path) -> None:
    """Preserve the prompt on stdin, the work directory, agent output and exit status."""
    install_skills(Path.cwd(), backend, repository)
    environment = {**os.environ, "ARIS_REPO": str(repository)}
    os.execvpe(command[0], command, environment)
