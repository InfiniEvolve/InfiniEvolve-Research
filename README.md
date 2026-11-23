# InfiniEvolve-Research

**InfiniEvolve 调度 Agent，ARIS 给 Agent 提供研究 skills。**

这个项目只负责在每个 Agent 启动前装好 skills。任务定义、工作目录、Agent 会话、候选选择、评估、停止、恢复和归档，都使用原版 [InfiniEvolve](https://github.com/InfiniEvolve/InfiniEvolve)。研究知识来自 [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)，以固定版本的 Git submodule 保留上游完整内容。

```text
InfiniEvolve 创建本次会话的工作目录
  → infinievolve-research agent 挂载 ARIS skills 和辅助文件
  → 原来的 Claude Code / Codex 执行任务
  → InfiniEvolve 评估、归档，决定下一次会话
```

## 安装

需要 Python 3.10+ 和 Git；真实运行还需要已登录的 Claude Code 或 Codex CLI。

```bash
git submodule update --init --recursive
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e vendor/InfiniEvolve -e .
```

请安装仓库里的 InfiniEvolve submodule：它固定了本项目验证过的核心版本。安装新项目不会更改上游代码，也不会覆盖用户全局的 skills 或 ARIS 配置。

## 按原来的方式使用 InfiniEvolve

```bash
infinievolve init projects/my-research
# 按 InfiniEvolve 的格式填写 task.yaml、evaluate.py 和 workspace/。
```

在生成的 `task.yaml` 中设置 Agent，把 `YOUR_MODEL` 换成当前账号可用的模型：

```yaml
agent:
  command: 'infinievolve-research agent --agent codex/YOUR_MODEL'
```

Claude Code 对应：

```yaml
agent:
  command: 'infinievolve-research agent --agent claude/YOUR_MODEL'
```

然后继续使用原来的命令：

```bash
infinievolve check projects/my-research --prompt
infinievolve run projects/my-research --sessions 6
infinievolve report projects/my-research
# 中断后接着跑；已有 run 的参数保存在 runs/default/config.yaml 中。
infinievolve run projects/my-research
```

已有 campaign 直接把 `config.yaml` 的 `agent` 改成上面的 `command` 即可。也可在任务第一次运行时用 `--agent-command 'infinievolve-research agent --agent codex/YOUR_MODEL'` 设置。保持虚拟环境已激活，让子进程能找到启动器。

`--agent` 会调用 InfiniEvolve 自己的 `agent_command()` 生成命令，因此模型、effort、输入输出和权限选项沿用核心实现。原版命名 Agent 使用跳过交互权限确认的参数；如需自行指定 CLI 选项，可直接传完整命令：

```bash
infinievolve-research agent --backend codex -- codex exec --json -m YOUR_MODEL -
```

## Agent 得到哪些 skills

| Agent | 原生发现目录 | 上游来源 | 当前固定版本数量 |
|---|---|---|---:|
| Claude Code | `.claude/skills/` | `vendor/aris/skills/` | 87 |
| Codex | `.agents/skills/` | `vendor/aris/skills/skills-codex/` | 87 |

包括文献检索、选题、新颖性检查、实验设计、运行与分析、研究评审、论文撰写等。使用原文并保留 `shared-references`、辅助脚本、模板和 Claude 的研究子 Agent 定义；通过 `ARIS_REPO` 环境变量告诉 Agent 上游仓库的位置。

启动器在 InfiniEvolve **创建会话工作副本之后**安装，因此每一次新会话都有 skills。知识库按需读取，不会把 87 个 SKILL.md 全部塞进 prompt。只排除 skill 链接、辅助文件链接和安装清单；`.aris/traces/` 等研究输出仍进入 InfiniEvolve 的结果补丁。

Skills 可读不代表其所有外部工具都已配置：搜索服务、评审 MCP、GPU 账号等仍按实际用到的 skill 配置。本项目不安装这些外部服务、不自动运行研究任务。

独立给一个工作目录安装 skills 也可以：

```bash
infinievolve-research install --backend codex --workspace /path/to/workspace
```

已有同名 skill 时会报冲突并保留原文件。对于 InfiniEvolve 任务，让启动器自动安装到临时会话目录即可，不要预装到 `workspace/` 基线里。可以用 `--aris-repo /path/to/aris` 或 `INFINIEVOLVE_RESEARCH_ARIS` 指定另一份完整 ARIS checkout。

## 本地验证

不调用模型、不需要 API key 的小例子：

```bash
infinievolve run examples/smoke --sessions 3
infinievolve report examples/smoke
```

这里的 Agent 是明确标注的脚本替身：检查 skills、共享参考、辅助脚本和模板是否可读，然后修改一个小程序。它验证真实的 InfiniEvolve 调度、工作副本、评估和归档链路，不代表真实模型的研究能力。

```bash
python -m pip install pytest
python -m pytest -q
```

测试覆盖 Claude/Codex 两种 skill 包的实际调度链路、下一会话继承、输出补丁恢复、结果记录保留和启动器输入/退出码透传。验证记录见 [docs/validation.md](docs/validation.md)。

## 上游边界

- `vendor/InfiniEvolve` 和 `vendor/aris` 都是固定版本、未修改的 submodule。
- 核心调度兼容性确实不足时，才单独修改 InfiniEvolve 并向其上游提 PR。本项目不维护私有核心补丁，也不自动合并 PR。
- 当前接入通过现成的 `agent.command` 扩展点完成，没有核心改动，也无需核心 PR。

来源、版本和许可证见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
