# llm-readable

A Claude Code plugin that makes any portfolio or website readable by LLMs.

Recruiters now screen portfolios with AI. ChatGPT, Perplexity and Claude answer "who is this person / what does this company do" from your site. These readers fetch raw HTML once, rarely run JavaScript, never look at your images, and often cut long pages short. If your site isn't built for them, they get an incomplete or wrong picture of you.

`/llm-readable` goes through your whole project and tells you exactly what an AI reader sees. Once you approve, it fixes what it can.

## What it does

1. **Reads everything:** every route, content file, data file, layout, image and config in your project.
2. **Looks at your site like a bot:** fetches it the way GPTBot or ClaudeBot does (no JavaScript) and measures what text, metadata and structured data actually arrive.
3. **Audits it:** scores ~40 checks across access, llms.txt, structured data, metadata, structure, content substance, media, payload and hygiene. You get a detailed **what's working** and **what's holding you back**, with evidence for each.
4. **Suggests next steps:** what it can fix now, what facts it needs from you (it never invents metrics or dates), and what to change in your hosting or CMS.
5. **Waits for your approval**, then fixes the items you picked: llms.txt and llms-full.txt generated from your content, sitemap, robots, title templates, descriptions, canonicals, JSON-LD, alt text written after looking at each image, noindex on unfinished pages, and more.
6. **Reports every change** against the problem it solves, with a before → after score.

It works with Next.js, Astro, Nuxt, SvelteKit, Remix, Gatsby, Vite/CRA SPAs, Hugo, Jekyll, Eleventy, plain HTML and WordPress themes. For Framer, Webflow, Wix and Squarespace it gives paste-ready snippets instead of editing files.

## Install

In Claude Code:

```
/plugin marketplace add vaibhavdotcv/skills
/plugin install llm-readable@vaibhav-skills
```

Then restart Claude Code.

## Update

```
/plugin marketplace update vaibhav-skills
/plugin update llm-readable@vaibhav-skills
```

Then restart Claude Code.

Not using Claude Code? Download [llm-readable.zip](https://github.com/vaibhavdotcv/skills/releases/download/latest/llm-readable.zip) and follow the steps for the [Claude app](../../README.md#claude-app-and-claudeai) or [other AI tools](../../README.md#other-ai-tools).

## Use

Open your site's project folder in Claude Code and run:

```
/llm-readable
```

You can also just ask: "make my portfolio LLM readable". To audit a live site without a repo, give it the URL: `/llm-readable https://example.com`.

Nothing is edited until you approve, and nothing is committed or deployed unless you ask.

## What's inside

```
skills/llm-readable/
├─ SKILL.md                    # the 8-phase workflow
├─ references/checklist.md     # the scored rubric (A1–I4)
├─ references/site-types.md    # what good looks like for portfolios, companies, blogs, docs, stores
├─ references/stacks.md        # where each fix goes, per framework
├─ references/report-format.md # audit, next steps and change-log templates
└─ scripts/bot_view.py         # see your site as an AI crawler (Python 3, no installs)
```

`bot_view.py` also works on its own:

```bash
python3 plugins/llm-readable/skills/llm-readable/scripts/bot_view.py https://example.com --sitemap 30 --pretty
```

## Requirements

- Claude Code
- Python 3.8+ for the crawler view (optional; it falls back to curl)
- ffmpeg or ImageMagick help it look at videos and large images (optional)

## License

MIT
