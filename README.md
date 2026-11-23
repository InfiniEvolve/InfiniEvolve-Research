# InfiniEvolve-Research

**InfiniEvolve runs the agent sessions. ARIS provides the research skills.**

```text
framework/               # InfiniEvolve, pinned Git submodule
skills/aris/             # ARIS, pinned Git submodule
scripts/with_skills.py   # Mount skills, then launch the agent
tests/                  # Integration tests with scripted stand-in agents
```

This project does not need to be installed as a Python package. Both submodules retain their complete upstream contents. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for sources and licenses.

## Setup

Requires Python 3.10+, Git, and a configured Claude Code or Codex CLI.

```bash
git submodule update --init --recursive
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e framework
```

This installs only the upstream InfiniEvolve package.

## Usage

Run from the root of this repository:

```bash
RESEARCH_ROOT="$(pwd)"
infinievolve init projects/my-research
# Fill in projects/my-research/task.yaml, evaluate.py, and workspace/.
# Replace YOUR_MODEL with a model available to your account.
infinievolve run projects/my-research --sessions 6 \
  --agent-command "python \"$RESEARCH_ROOT/scripts/with_skills.py\" codex/YOUR_MODEL"
```

For Claude Code, replace `codex/YOUR_MODEL` with `claude/YOUR_MODEL`. You can append `:EFFORT` to the model name. The script reuses InfiniEvolve's agent commands and their CLI options. The upstream agent presets bypass interactive permission prompts. To supply your own options, pass a full command with `with_skills.py codex -- codex exec ...` or `with_skills.py claude -- claude ...`.

For an existing campaign, set `agent.command` in `config.yaml` using the script's absolute path:

```yaml
agent:
  command: 'python "/absolute/path/to/InfiniEvolve-Research/scripts/with_skills.py" codex/YOUR_MODEL'
```

Keep the virtual environment activated. Use the standard commands to view results or resume a run. For an existing run, omit the configuration flags used when it was first created:

```bash
infinievolve report projects/my-research
infinievolve run projects/my-research
```

## How skills are mounted

After InfiniEvolve creates a session's working copy, the script creates local symlinks to ARIS and launches the agent. It does not download the skills again, change global user configuration, or overwrite existing skills with the same names.

| Agent | Directory in the session workspace | Skills at the pinned revision |
|---|---|---:|
| Claude Code | `.claude/skills/` | 87 |
| Codex | `.agents/skills/` | 87 |

Shared references, helper scripts, templates, and Claude's research subagent definition are mounted alongside the skills. `ARIS_REPO` points to the upstream checkout. Only dependency links are excluded from the captured patch; research records such as `.aris/traces/` are still archived by InfiniEvolve. Configure external services, such as search providers, reviewer MCP servers, and GPU access, as required by the skills you use.

## Validation

```bash
python -m pip install pytest
python -m pytest -q tests
```

The tests use the real InfiniEvolve scheduler with scripted stand-in agents. They cover both skill packs, archiving and inheritance of results, repeated mounting, preservation of existing skills, and forwarding of the original input and exit code. Passing these tests alone does not establish that a real model has used the skills.

The InfiniEvolve core remains unchanged. Any necessary compatibility change must be submitted separately as an upstream pull request.
