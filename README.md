# Skills for designers and engineers

Skills I've built, in one place. They work best in Claude Code, and also in the Claude app and other AI tools.

## Skills

| Skill | What it does | Download |
|---|---|---|
| [llm-readable](plugins/llm-readable) | Audits a portfolio or website for how well LLMs and AI screeners can read it, then fixes what's holding it back. | [llm-readable.zip](https://github.com/vaibhavdotcv/skills/releases/download/latest/llm-readable.zip) |

The examples below use `llm-readable`. For any other skill, swap in its name.

Jump to: [Claude Code](#claude-code) · [Claude app and claude.ai](#claude-app-and-claudeai) · [Other AI tools](#other-ai-tools)

## Claude Code

### Install

Inside [Claude Code](https://claude.com/claude-code):

1. Add this marketplace (only once):

   ```
   /plugin marketplace add vaibhavdotcv/skills
   ```

2. Install a skill:

   ```
   /plugin install llm-readable@vaibhav-skills
   ```

3. Restart Claude Code.

### Use

Open your project in Claude Code and type the skill's name:

```
/llm-readable
```

Or just ask in plain words, like "make my portfolio LLM readable".

### Update

```
/plugin marketplace update vaibhav-skills
/plugin update llm-readable@vaibhav-skills
```

Then restart Claude Code. The first line also brings in any new skills, which you can install the same way as above.

### Remove

```
/plugin uninstall llm-readable@vaibhav-skills
```

To remove the marketplace too: `/plugin marketplace remove vaibhav-skills`.

## Claude app and claude.ai

Skills need code execution turned on in your Claude settings.

### Install

1. Download the skill's zip from the [Skills](#skills) table above.
2. In Claude, open **Settings → Capabilities → Skills** and upload the zip as it is. Don't unzip it.

### Use

Ask for it in any chat, like "check how readable vaibhav.cv is for LLMs". Claude picks up the skill when it fits.

In a chat, Claude can't see or edit your project files. It can audit a live website and tell you what to change, but you'll apply the changes yourself.

### Update

Download the zip again (the link always points to the newest version). In **Settings → Capabilities → Skills**, delete the old one and upload the new zip.

### Remove

In **Settings → Capabilities → Skills**, delete the skill, or switch it off to keep it for later.

## Other AI tools

Many AI coding tools, like Codex, Cursor and Gemini CLI, can read skills too. Each skill is a folder with a `SKILL.md` file inside. Check your tool's docs for where its skills folder is.

### Install

Download the skill's zip from the [Skills](#skills) table above, unzip it, and move the `llm-readable` folder into your tool's skills folder.

### Use

Open your project in the tool and ask for it in plain words, like "make my portfolio LLM readable". Some tools also let you call a skill by name.

### Update

Download the zip again, then replace the old `llm-readable` folder with the new one.

### Remove

Delete the `llm-readable` folder from your tool's skills folder.

## License

MIT
