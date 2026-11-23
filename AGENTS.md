# Project instructions

- 说人话。
- 如果做了实验，用表格或者图总结结果，并用一到两段话说明设置、结果和分析。
- 发邮件前必须找用户 double check。
- 本项目只给 InfiniEvolve 启动的 Agent 安装 ARIS skills。不要擅自增加研究阶段调度器、评分体系或新的工作流框架。
- InfiniEvolve 是唯一核心调度框架。只有核心兼容性确实需要时才能改动 `vendor/InfiniEvolve`，并且必须单独向上游提 PR；不要在本项目偷偷保留核心补丁。
- 保留 ARIS 上游 skills 原文及其依赖。不要覆盖用户已有的同名 skills 或全局配置。
- 脚本替身验证与真实模型运行必须明确区分。

Validation: activate `.venv`, then `python -m pytest -q`. Dependencies are pinned Git submodules;
install with `python -m pip install -e vendor/InfiniEvolve -e .`.
