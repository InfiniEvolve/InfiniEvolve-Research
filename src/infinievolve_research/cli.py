"""A skill installer and agent launcher; scheduling stays in InfiniEvolve."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .runtime import BACKENDS, aris_repository, install_skills, launch


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    install = sub.add_parser("install", help="install native skills in an existing workspace")
    install.add_argument("--backend", choices=BACKENDS, required=True)
    install.add_argument("--workspace", type=Path, default=Path.cwd())
    install.add_argument("--aris-repo")
    agent = sub.add_parser("agent", help="install skills, then replace this process with the agent")
    choice = agent.add_mutually_exclusive_group(required=True)
    choice.add_argument("--agent", help="the existing InfiniEvolve agent spec: codex/model or claude/model[:effort]")
    choice.add_argument("--backend", choices=BACKENDS, help="skill pack for a custom command after --")
    agent.add_argument("--aris-repo")
    agent.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    try:
        repository = aris_repository(args.aris_repo)
        if args.action == "install":
            manifest = install_skills(args.workspace, args.backend, repository)
            print(json.dumps(manifest, indent=2))
            return 0
        command = args.command[1:] if args.command[:1] == ["--"] else args.command
        if args.agent:
            if command:
                raise ValueError("--agent cannot be combined with a custom command")
            from infinievolve.local import agent_command
            command, shell = agent_command(args.agent)
            backend = args.agent.split("/", 1)[0]
            if shell:
                raise ValueError("use --backend and a command after -- for a custom agent")
        else:
            backend = args.backend
            if not command:
                raise ValueError("--backend requires a command after --")
        launch(backend, command, repository)
    except (ValueError, OSError) as error:
        print(f"infinievolve-research: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
