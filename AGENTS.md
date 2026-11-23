# Project instructions

- Use plain language.
- When running experiments, summarize the results in a table or chart, with one or two paragraphs explaining the setup, results, and analysis.
- Get the user's confirmation before sending any email.
- This project only installs ARIS skills for agents launched by InfiniEvolve. Do not add research-stage schedulers, scoring systems, or new workflow frameworks without explicit authorization.
- InfiniEvolve is the sole core scheduling framework. Modify `framework` only when core compatibility requires it, and submit those changes in a separate upstream PR. Do not keep undisclosed core patches in this project.
- Preserve the original upstream ARIS skills and their dependencies. Do not overwrite the user's existing skills with the same names or their global configuration.
- Clearly distinguish validation with scripted stand-ins from runs using real models.

Validation: activate `.venv`, then `python -m pytest -q tests`. Dependencies are pinned Git submodules.
Install only the core with `python -m pip install -e framework`; this project has no Python package.
Keep runtime integration in the single `scripts/with_skills.py` script.
