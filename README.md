# Vaibhav's skills

Claude Code skills I've built, in one place. Add the marketplace once, then install the ones you want.

## Install

In Claude Code:

```
/plugin marketplace add vaibhavdotcv/skills
/plugin install <skill>@vaibhav-skills
```

Restart Claude Code after installing. To get new skills and updates later, run `/plugin marketplace update vaibhav-skills`, then `/plugin update <skill>`.

## Skills

| Skill | What it does | Install |
|---|---|---|
| [llm-readable](plugins/llm-readable) | Audits a portfolio or website for how well LLMs and AI screeners can read it, then fixes what's holding it back. | `/plugin install llm-readable@vaibhav-skills` |

## Adding a skill (for me)

1. Create `plugins/<name>/.claude-plugin/plugin.json` and `plugins/<name>/skills/<name>/SKILL.md`.
2. Add an entry to `.claude-plugin/marketplace.json` with `"source": "./plugins/<name>"`.
3. Add a row to the table above.
4. Run `claude plugin validate .` and bump `version` in the plugin's `plugin.json` on every change.

## License

MIT
