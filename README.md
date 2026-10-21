# Skills for designers and engineers

Claude Code skills I've built, in one place. Add the marketplace once, then install the ones you want.

## Skills

| Skill | What it does | Install |
|---|---|---|
| [llm-readable](plugins/llm-readable) | Audits a portfolio or website for how well LLMs and AI screeners can read it, then fixes what's holding it back. | `/plugin install llm-readable@vaibhav-skills` |

## Install

You'll need [Claude Code](https://claude.com/claude-code). Then, inside Claude Code:

1. Add this marketplace (only once):

   ```
   /plugin marketplace add vaibhavdotcv/skills
   ```

2. Install a skill:

   ```
   /plugin install llm-readable@vaibhav-skills
   ```

3. Restart Claude Code.

## Use

Open your project in Claude Code and type the skill's name, for example:

```
/llm-readable
```

Or just ask for it in plain words, like "make my portfolio LLM readable".

## Update

To get the latest version of a skill:

```
/plugin marketplace update vaibhav-skills
/plugin update llm-readable@vaibhav-skills
```

Then restart Claude Code. The first line also brings in any new skills I've added since, which you can install the same way as above.

## Remove

```
/plugin uninstall llm-readable@vaibhav-skills
```

To remove the marketplace too: `/plugin marketplace remove vaibhav-skills`.

## License

MIT
