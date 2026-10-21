---
name: llm-readable
description: Audit a portfolio or website for how well LLMs, AI search and AI recruiting/screening tools can read it, report what helps and what hurts with evidence, propose next steps, then (after the author approves) fix them and report every change. Works on any stack - Next.js, Astro, Nuxt, SvelteKit, Gatsby, Vite SPAs, Hugo, Jekyll, 11ty, plain HTML, WordPress, and site builders like Framer or Webflow (advice mode). Use when someone asks to make their site/portfolio "LLM readable", "AI readable", "AI-ready", optimised for AI screeners or recruiters, for GEO/AEO/LLM SEO, or to add llms.txt, structured data or alt text for AI.
---

# Make a site LLM-readable

AI tools increasingly read a site before any human does: a recruiter's pipeline
screening 100 portfolios, ChatGPT/Perplexity/Claude answering "who is X / what does Y
do", agents following links. They fetch raw HTML once, rarely run JavaScript, never look
at images, and often truncate long pages. This skill makes sure such a reader gets the
**complete, correct and attributable** picture of the site.

The run has nine phases. Phases 0–4 only read; nothing is edited until the author
approves in Phase 5. Keep the author posted with one short line as each phase starts.

Reference files (read them when the phase needs them, not all up front):
- `references/checklist.md`: the scored rubric (check IDs A1–I4). **The source of truth for what to check.**
- `references/site-types.md`: content expectations per site type (portfolio, company, blog, docs, store).
- `references/stacks.md`: where each fix goes, per framework.
- `references/report-format.md`: templates for the audit, next steps and change log.
- `scripts/bot_view.py`: fetches pages the way an AI crawler does and measures them (Python 3 stdlib only).

Paths above are relative to this skill's directory. Run the script with its full path.

---

## Ground rules (apply throughout)

1. **Never invent facts.** Metrics, outcomes, dates, titles, team sizes, skills, locations and employers come from the site's own content or from the author. If they're missing, that's a finding plus a question, never a placeholder like "increased conversion by 30%".
2. **Look before describing.** Write alt text or media descriptions only after viewing the image or a video frame. Never describe from a filename.
3. **Preserve the author's voice, facts and design.** No visual or copy changes beyond what was approved. Reuse the site's own copy for descriptions where it exists. When you write new text (alt text, one-liners), keep it plain and factual, and list it for review.
4. **Neutral pronouns.** Refer to the author by name or as "they" unless their pronouns are stated on the site. When you carry the author's first-person words into third-person files (llms.txt, JSON-LD descriptions), quote them ("In Name's words: \"…\"") instead of rewriting "me" as "him"/"her".
5. **Respect deliberate choices.** If robots.txt blocks AI crawlers on purpose, or pages are noindexed on purpose, report it and ask. Don't "fix" it silently.
6. **Follow the project's conventions and docs.** Read AGENTS.md / CLAUDE.md / CONTRIBUTING and the installed framework's own docs before writing code. Framework APIs differ by version (see stacks.md).
7. **Safe by default.** Never commit, push, deploy, delete pages, install dependencies or touch secrets/.env without explicit approval. Don't run the author's long-running dev server in the foreground. Use the build command or an existing preview.
8. **Evidence over opinion.** Every finding cites a file:line, a URL, or a measured number.
9. **Check what's rendered, not just the data.** A field in a data file may never reach the page (a component can hide it, ignore it or drop a prop). Before saying visitors or crawlers see something, or proposing a visible fix for it, confirm it in the built HTML or a screenshot.
10. **The author decides where each fact goes.** Some facts are public, some are for AI readers only (e.g. a tools list they don't want on the page), and some stay private (e.g. metrics shared over email). Keep AI-only facts in the identity source so they reach llms files and JSON-LD but not the UI. For private facts, write the fallback the author gives ("metrics on request: email …") and score the check Partial by their choice. Never push them to publish.

---

## Phase 0: Orient

1. Find the project root (the folder with the framework config / package.json / site config). If the user pointed at a URL only and there's no repo, switch to **advice mode**: audit the live site and produce paste-ready fixes (stacks.md → site builders).
2. Run `git status`. If there are uncommitted changes, tell the author and suggest a branch before Phase 6; never discard or stash their work without asking. If it's not a git repo, warn that changes can't be rolled back easily.
   - **Working tree vs production.** If the uncommitted or unpushed changes are large, the live site and the repo are different sites. Audit the one the author will ship (usually the working tree, through a local build), use the live site only for host, redirect and DNS checks, and say which one you scored in "How I checked".
3. Detect the stack and version: package.json dependencies and lockfile; config files (`next.config.*`, `astro.config.*`, `nuxt.config.*`, `svelte.config.*`, `gatsby-config.*`, `remix.config.*`/`react-router.config.*`, `vite.config.*`, `hugo.*`/`config.toml`, `_config.yml`, `.eleventy.*`, `wp-content`/`style.css` theme header); or plain `index.html`. Note the rendering mode (SSG / SSR / SPA).
4. Read the repo's agent and contributor docs (AGENTS.md, CLAUDE.md, README, CONTRIBUTING) and any framework docs shipped in node_modules that they point to.
5. Find the production URL. Collect **every** candidate: metadata/site config (`metadataBase`, `site`, `baseURL`, `url`), CNAME, vercel/netlify config, package.json `homepage`, README, footer/social links, hard-coded absolute URLs in pages. Config values go stale after domain changes, so don't trust the first one you find. If the candidates disagree, fetch each, follow its redirects, and raise the mismatch as a canonical-host question (D3/I2). If you can't find any, ask once. It's fine to continue without it.
6. Classify the site type using `references/site-types.md` (it can be mixed).

## Phase 1: Gather context end to end

The goal is to know the site as well as its author. **Read, don't skim.**

1. **Route inventory.** List every page/route, including dynamic routes and the data that generates them (slugs, collections, CMS queries). Include API/feed/file routes. Note which routes look unfinished: playground, sandbox, test, draft, demo, `old`, `v2`, lorem ipsum, placeholder data. **Placeholder data often looks real**: template milestones with specific numbers ("spoke at a conference to 300 people", "lifted activation by 18%", "crossed 2,000 users"), lists of plausible project names that all link to the same URL, roles that contradict the experience page. Cross-check every claim against the rest of the site; anything not backed up elsewhere is a question for the author, not a fact. Also note test copies of real pages (e.g. a "test case study"), which are duplicates (I3). Also check how navigation renders: a navbar or menu that returns `null` until mounted, renders only in `useEffect`, or loads on click hides every internal link from crawlers (A8).
2. **Content.** Read the content sources: markdown/MDX, JSON/JS/TS/YAML data files, CMS fetch code (and sample responses if cached), copy hard-coded in components and layouts, OG image templates, résumé PDFs.
   - **Read in full:** the home page, about/bio, experience/résumé, and every case study, product or service page (whatever carries the site's core claims).
   - **Read for facts and dates:** blog posts/notes, lab/experiment entries, changelogs. Skim the prose, but note every name, role, date, company and claim.
   - Build a short fact sheet as you go: name, current title, employer, past roles with dates, projects with role/team/duration/outcome/date, skills, location, contact links. Note every place a fact appears, because inconsistencies are findings (C3). Cross-check dates: a project dated after the job that produced it ended, or a publish date presented as a project date, is a finding (F5).
   - Use the "common gaps" list for the site type in `references/site-types.md` as you read.
3. **Metadata and head.** Root layout/head, per-page metadata, title templates, canonical, OG, `lang`, existing JSON-LD, robots/sitemap/llms files or generators, redirects (framework config, `_redirects`, `vercel.json`, `netlify.toml`).
4. **Media.** List every image/video referenced by content with its alt/label status (missing, empty, generic like "image", duplicated, or **wrong**: e.g. a team photo labelled "product design work"). First find the site's image/media component and its default `alt`. Many default to `alt=""`, so a data entry with **no alt field** renders as empty alt, which bot_view reports as `images_empty_alt_suspect` rather than missing. Count entries without an alt key directly in the content/data files. Also check the media component **passes** the label on: video players often ignore `alt`, so a data entry can have a label that never reaches the `<video>` (`aria-label`).
5. **Links.** Note fake or placeholder hrefs (`#`, google.com, example.com), broken internal links and mixed hosts.
6. **Coverage.** On big repos, split the reading by area (e.g. by top-level route or content folder). Use subagents if the environment offers them; otherwise go area by area. Keep a checklist of areas read so nothing is skipped, and say in the report what was read.

## Phase 2: See what a machine sees

1. Run the crawler view on the live site (and on a local build or preview if one is available or cheap to produce):
   ```bash
   python3 <skill-dir>/scripts/bot_view.py <url> --sitemap 40 --pretty > /tmp/bot_view.json
   ```
   Paths can go before or after the options. **Without a sitemap, bot_view only sees the paths you pass it.** Pass every route from the Phase 1 inventory (at least one per route group, including playground/test routes): `bot_view.py <url> /about /work/<slug> …`. Try `--ua claudebot` as well if anything looks blocked.
   **Check every host variant yourself**: apex and `www` of every domain you found in Phase 0 (`curl -sI <url>` for each). bot_view only follows the base URL's redirects. Look for 307/302 (temporary), a second domain that serves the whole site with 200, and chains where a domain redirects to its own `www`, which then serves the site.
   The script prints **score hints** to stderr (e.g. `A4:FAIL  D2:ok  G1:part`) and puts them in `summary.score_hints`. `check` means "confirm in the source before scoring".
2. For a local check, prefer the stack's production build plus its preview/start command on a free port, or inspect the built HTML files directly. Don't kill or reuse the author's running dev server without asking.
3. Read the JSON: the `summary` first, then `pages` for anything suspicious. Map fields to checks using the table at the end of checklist.md.
4. **Local-only failures aren't site bugs.** If a page returns 500 or errors only on the local build, read the server log. Missing env vars (database, Redis, API keys), unseeded data and auth-only services are local artefacts. Note them under "Caveats", check the live page if possible, and don't score them as A5 failures.
5. If neither live nor local fetch is possible (no network, no build), do the audit statically and say so in "How I checked".
6. If `python3` isn't available, use `curl -sL -A "GPTBot" -D - <url>` and inspect the HTML by hand for the same signals.

## Phase 3: Audit report

1. Score every check in `references/checklist.md` as Pass / Partial / Fail / N/A (with a reason), using Phase 1 and 2 evidence. Start from bot_view's `score_hints`, confirm each against the source, then score the remaining (static/content) checks. Fill in the score sheet at the end of checklist.md so the tally is exact. Category F uses the questions for the site's type from site-types.md.
   - Use each check's listed severity unless the evidence clearly says otherwise (e.g. a fake link in a draft page vs on the home page). Say why if you change it.
   - Routes that 404 on purpose (removed pages, redirects) aren't failures. Missing pages that are linked are.
2. Write the report using the template in `references/report-format.md` § 1: score table, **What's working for you**, **What's holding you back** (severity + fix type + check IDs + evidence + why it matters).
3. Go deep. The author asked for detail: name the specific pages, sentences, images and numbers. But don't pad: merge duplicates and skip trivia.
4. Cite numbers from bot_view; don't paste raw JSON into the report.

## Phase 4: Next steps

Write the plan using report-format.md § 2, in three groups:
- **I can do now:** auto-fixable items, with files that will be touched and whether anything changes visually.
- **Needs your input:** missing facts, as specific questions (what, why, where it will go).
- **Outside the repo:** hosting/DNS/CMS/site-builder steps with exact settings.

End with the expected score after all steps, and anything that would still fail and why.

## Phase 5: Approval gate

Ask before editing anything. If an `AskUserQuestion`-style tool is available, use it:
- A multi-select of the fix groups from "I can do now" (recommend all; flag anything with a visible change or a deletion separately).
- A question inviting the facts from "Needs your input" (they can answer now, later, or skip).
- Any judgement calls: canonical host (apex vs www), what to do with placeholder pages (keep and noindex, keep only the real items, or delete), whether AI crawlers should be allowed.
- The author may answer with something other than the options you offered. Follow what they actually said, and if a question goes unanswered, leave that item alone and say so.

Without such a tool, ask in plain text and wait. **Don't proceed on silence.** If the author approves only some items, do only those.

## Phase 6: Implement

Work through the approved items, highest severity first. Follow `references/stacks.md` for the stack and the repo's own patterns (naming, file layout, comment density, quote style).

Patterns that make the fixes last:
1. **One identity source** (name, title, employer, summary, links, skills, location, availability, canonical `SITE_URL`, plus any AI-only facts such as tools) imported by metadata, JSON-LD, sitemap and llms builders. Reuse an existing site config if there is one.
2. **One content-flattening helper** that turns the site's content into plain text/markdown. Reuse existing RSS/search-index code if present.
3. **llms.txt and llms-full.txt generated from content at build time** (B1–B3). Hand-written files only for stacks with no build step, and say so.
4. **Metadata:** title template, per-page descriptions from existing copy, canonicals on the host that serves 200.
5. **Structured data:** Person/Organization site-wide with a stable `@id`; per-page CreativeWork/BlogPosting/Product referencing it.
6. **Crawl control:** robots + sitemap generated from the route inventory; unfinished pages noindexed **and** excluded from sitemap and llms. Don't also `Disallow` a noindexed path in robots.txt if it may already be indexed: crawlers that can't fetch the page never see the noindex.
7. **Media:** view each image (downscale big ones first, e.g. `sips -Z 800` on macOS, ffmpeg or ImageMagick elsewhere), then write alt text that says what it shows and why it's there. Video: extract two frames (around 30% and 70% of the duration) and set an aria-label/caption; add `-vf format=yuvj420p -strict unofficial` if ffmpeg refuses to write the JPEG. For dozens of small items (a lab or gallery), tile frames into contact sheets (ffmpeg `xstack`) to view several at once. If no tool can extract frames, ask the author for a one-line description.
   - Don't name people in photos or read out number plates, addresses or other personal details; describe the scene ("group photo of the team in the office cafeteria").
   - Mark purely decorative images (an avatar repeated next to its own text) `alt=""` plus `aria-hidden`.
   - Give side projects one-line descriptions you can reuse in llms.txt, so the same text does both jobs.
8. **Facts from the author:** apply them exactly as given, everywhere the fact appears. Things you can derive from the site itself aren't invented, so derive them instead of asking again. For example, link each case study to the job it was done in, then state "done as <role> (<tenure>)" and label any write-up date as the published date.
9. **Small content fixes** (typos in headings, copy-paste leftovers, fake links) only if approved. List each one.
10. **No-visual-change fixes:** prefer fixes that change nothing on screen.
   - Nav hidden before hydration: render the same links as a visually hidden list until mounted.
   - Skipped heading levels: change the tag only after checking the class sets its own font and margins are reset, and that nothing selects headings by tag (tables of contents, scroll spies).
   - Missing `<main>`: swap the page's root `div` for `main` (check no CSS targets `main`).
   - When you edit a shared component, check every page that uses it.

Keep a running list of every change against the audit item it addresses, for Phase 8.

## Phase 7: Verify

1. Run the project's build (and lint/typecheck if the project has them) and fix anything you broke. Report failures honestly if they're pre-existing: compare against the same files at `HEAD`, and name which errors are yours and which aren't.
2. Re-run `bot_view.py` against the local build/preview (or inspect the generated HTML and files). Confirm: llms files return text (not an HTML catch-all), robots/sitemap are correct, titles/descriptions/canonicals/JSON-LD are present, alt text is there, noindex is where intended.
3. Open llms.txt and skim llms-full.txt: correct facts, absolute URLs on the canonical host, no unfinished pages, no first-person/third-person mix-ups.
4. For any change visitors can see, open the page in a browser and screenshot it. Wait for entrance animations to finish first: a blank or blurred screenshot is usually mid-animation, not broken.
5. When the author says they've done a step outside the repo (DNS, hosting redirects), check it yourself (`curl -sI` every host) before marking it done.
6. Re-score the checklist. If anything regressed, fix it before reporting. Say whether the score is for the local build or the live site: changes only count for AI readers once deployed.

## Phase 8: Change log

Write it using report-format.md § 3:
- A **problem → change table** where every "holding you back" item appears exactly once, with status (Fixed / Partly / Needs you / Outside repo / Skipped by choice), what changed and the files.
- Before → after score, new files, things the author should review (anything written in their name), and what's still open with the exact next action.
- State clearly that nothing was committed or deployed (unless the author asked for that).

Offer, in one line each: committing the changes on a branch, and re-running the audit after the author fills in the missing facts.

## Phase 9: Further rounds

Audits rarely finish in one pass: the author approves more fixes, answers questions or completes platform steps over several messages.
- End every round with the current score, what's left, and roughly what each remaining item is worth ("fixing X takes it to ~85%"), split into what you can do and what needs the author.
- When they approve more, run Phases 6–8 for just those items and give an updated score and a short change log, not the whole report again.
- After they deploy, offer to re-run bot_view against the live site to confirm the score holds there.
