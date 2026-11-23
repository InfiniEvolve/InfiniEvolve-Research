# InfiniEvolve-Research

**InfiniEvolve 负责调度，ARIS 提供研究 skills。**

```text
framework/                # InfiniEvolve，固定版本的 submodule
skills/aris/              # ARIS，固定版本的 submodule
scripts/with_skills.py    # 挂载 skills，再启动 Agent
tests/                   # 接入测试，模型使用脚本替身
```

项目本身不需要安装成 Python 包。两个 submodule 保留完整上游内容，来源和许可证见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 准备

需要 Python 3.10+、Git，以及已配置的 Claude Code 或 Codex CLI。

```bash
git submodule update --init --recursive
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e framework
```

这里只安装原版 InfiniEvolve。

## 使用

在本仓库根目录运行：

```bash
RESEARCH_ROOT="$(pwd)"
infinievolve init projects/my-research
# 填写 projects/my-research/task.yaml、evaluate.py 和 workspace/。
# 将 YOUR_MODEL 换成账号可用的模型。
infinievolve run projects/my-research --sessions 6 \
  --agent-command "python \"$RESEARCH_ROOT/scripts/with_skills.py\" codex/YOUR_MODEL"
```

Claude Code 把 `codex/YOUR_MODEL` 换成 `claude/YOUR_MODEL`；模型后面可以加 `:EFFORT`。脚本复用 InfiniEvolve 的 Agent 命令，沿用其 CLI 选项。核心的命名 Agent 默认跳过交互权限确认；需要自定义选项时，用 `with_skills.py codex -- codex exec ...` 或 `with_skills.py claude -- claude ...` 传入完整命令。

已有 campaign 只需设置 `config.yaml` 的 `agent.command`，使用脚本的绝对路径：

```yaml
agent:
  command: 'python "/absolute/path/to/InfiniEvolve-Research/scripts/with_skills.py" codex/YOUR_MODEL'
```

保持虚拟环境已激活。查看结果和恢复运行仍用原来的命令，已有 run 不再重复传首次配置参数：

```bash
infinievolve report projects/my-research
infinievolve run projects/my-research
```

## 挂载方式

InfiniEvolve 建好本次会话的工作副本后，脚本创建指向 ARIS 的本地链接，再执行 Agent。不会每次重新下载，也不改用户的全局配置或覆盖同名 skills。

| Agent | 会话中的目录 | 固定版本的 skills 数量 |
|---|---|---:|
| Claude Code | `.claude/skills/` | 87 |
| Codex | `.agents/skills/` | 87 |

共享参考、辅助脚本、模板和 Claude 的研究子 Agent 定义一并挂载；`ARIS_REPO` 指向上游仓库。只排除依赖链接，`.aris/traces/` 等研究记录仍由 InfiniEvolve 归档。搜索、评审 MCP、GPU 等外部服务按实际使用的 skill 另行配置。

## 验证

```bash
python -m pip install pytest
python -m pytest -q tests
```

测试使用真实 InfiniEvolve 调度器和脚本替身 Agent，覆盖两种 skill 包、结果归档与继承、重复挂载、已有 skill 保留，以及原始输入和退出码透传。测试通过不等同于真实模型已经调用过这些 skills。

InfiniEvolve 核心保持原样；只有确实需要核心兼容性改动时，才单独向上游提 PR。
