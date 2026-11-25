# Definition of Done

## Requirements

- [ ] Validator self-tests pass: `bash tests/selftest.sh`
- [ ] The plugin structure is valid and free of client names: `PM_SKILLS_FORBIDDEN_TERMS=<local file> bash tests/validate.sh`, run with the variable set
- [ ] Script and hook tests pass: `python3 -m unittest discover -s tests -p 'test_*.py'`
- [ ] The manifest schema is valid: `claude plugin validate . --strict`
- [ ] Every skill or agent added or changed has its scenarios in `tests/scenarios/<component>/` run, with the date and outcome recorded there
- [ ] A pull request that changes what the plugin does bumps `version` in `.claude-plugin/plugin.json` (see `AGENTS.md` for patch, minor or major)
- [ ] `README.md` is updated when a skill, agent or hook is added, renamed or removed; a new or changed skill has a README that follows the `skill-maker` contract
- [ ] A skill, agent or hook added or changed follows `DESIGN.md`; a pull request that adds, renames or removes a skill updates the coverage map there
- [ ] Descriptions, READMEs and examples of skills and agents are in English; an Italian term a skill adds or changes is in `shared/glossary/it.md`
- [ ] A pull request that adds or changes a skill has had its description and its context use reviewed with the `skill-creator` skill, without changing behavior; the pull request description says what was reviewed and what changed
- [ ] The pull request is merged into `main`, with the `validate` check green

## On Done

- After a merge that changed the plugin, bring the local install in line with `main`: `claude plugin marketplace update mrbogomips`, then `claude plugin update pm-skills@mrbogomips`, and check that `claude plugin list` shows the version in `plugin.json`. Sessions already open pick it up after a restart.
- Ask before acting when the plugin is installed at project scope or from another source.
