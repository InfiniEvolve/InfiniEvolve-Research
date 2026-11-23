# Upstream projects

| Role | Project | Pinned commit | License |
|---|---|---|---|
| Scheduler | [InfiniEvolve/InfiniEvolve](https://github.com/InfiniEvolve/InfiniEvolve) | `19a95f4061f2bd47f50a773e6c3f2a0273118c26` | MIT, [upstream license](framework/LICENSE) |
| Research skills | [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | `4ba94ae2a1c1fbbb14858750dd8764cabf6c28bd` | MIT, [upstream license](skills/aris/LICENSE) |

Both repositories are included unchanged as Git submodules. Their original copyright notices,
licenses and any notices for embedded third-party material remain in those repositories.

[NVlabs/kda](https://github.com/NVlabs/kda/tree/acdd79343c5e9d0c7cb96289f26fd3f1051ce785)
was read as an architectural reference for composing an agent workflow with pinned skill libraries.
No KDA source, prompts, documentation or assets are copied into this project.

Relevant integration interfaces:

- [InfiniEvolve's local adapter and agent command](https://github.com/InfiniEvolve/InfiniEvolve/blob/19a95f4061f2bd47f50a773e6c3f2a0273118c26/infinievolve/local.py)
- [ARIS agent guide](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/blob/4ba94ae2a1c1fbbb14858750dd8764cabf6c28bd/AGENT_GUIDE.md)
- [ARIS Codex skill package](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/tree/4ba94ae2a1c1fbbb14858750dd8764cabf6c28bd/skills/skills-codex)
