# 接入验证

日期：2026-11-23。环境：macOS、Python 3.13.13、pytest 9.2.0。项目使用独立 `.venv`，本次安装复用了本机已有的 Python 依赖（`--system-site-packages`），并以 editable 方式安装两个本地包。InfiniEvolve 固定在 `19a95f4061f2bd47f50a773e6c3f2a0273118c26`，ARIS 固定在 `4ba94ae2a1c1fbbb14858750dd8764cabf6c28bd`。

这是软件接入测试。使用真实 InfiniEvolve 调度器、工作副本、评估器和归档，只把调用模型的部分换成确定性脚本；没有调用真实模型、外部评审、搜索服务或 GPU，也没有开展科研实验。

| 检查项 | 结果 |
|---|---|
| `python -m pytest -q` | 6 passed，8.70 秒 |
| Codex 包 | 每次 Agent 会话中 87/87 个 SKILL.md 可读 |
| Claude Code 包 | 每次 Agent 会话中 87/87 个 SKILL.md 可读 |
| 共享参考、helper、模板 | 均可从会话工作目录读取 |
| 原始 prompt、环境变量、退出码 | 正确透传；自定义命令返回 23，启动器也返回 23 |
| 命名 Agent | 直接复用核心 `agent_command()` 的命令 |
| 代码与研究记录归档 | `solution.py` 和 `.aris/traces/smoke.json` 保留在结果补丁里 |
| 安装内容归档 | skills / helpers 的链接和安装清单不混入结果补丁 |
| 后续会话 | 从前次候选补丁恢复，评估值一致 |
| 重复安装、已有 skill | 重复安装结果一致；同名用户文件不被覆盖 |
| 完成后的再次运行 | 复用已有归档，不追加会话 |
| 两个上游 submodule | 工作树均无修改 |

另外直接运行了 README 中的命令：

```bash
source .venv/bin/activate
infinievolve run examples/smoke --sessions 3
infinievolve report examples/smoke
```

| 会话 | 角色 | MSE | 验证 |
|---|---|---:|---|
| s000 | 原始基线，prediction = 0 | 4.666667 | 有效 |
| s001 | 脚本设 prediction = 2 | 0.666667 | 有效；87 个 Codex skills 可读 |
| s002 | 继承 s001 | 0.666667 | 有效；核心标记为重复候选 |
| s003 | 继承 s001 | 0.666667 | 有效；达到 3 次会话上限 |

小例子在固定目标 `[1, 2, 3]` 上计算均方误差，最优常数 2 是脚本预设的。因此这些数字只证明启动、skill 挂载、候选继承、干净副本评估和停止机制连通，不能用来说明 Agent 会研究或会优化。真实 Claude/Codex 的 skill 调用行为及外部工具配置尚未做在线验证。

测试输出中的一个 warning 来自本机已有的 anyio pytest 插件使用了 pytest 将废弃的别名，不影响这 6 项验证。
