# LLM-readability checklist

The scored rubric. Every check has an ID, the reason it matters to an LLM reader,
how to detect it (static = reading the repo, bot = `scripts/bot_view.py` output),
how to fix it, and whether you can fix it yourself.

**Fix types**
- `auto`: you can fix it in the repo without new facts from the author.
- `input`: needs facts only the author has (metrics, role, dates, skills, location). Never invent them.
- `platform`: lives outside the repo (DNS, hosting, CMS, site builder settings). Give exact steps.

**Scoring.** Each check is Pass / Fail / Partial (counts as half) / N/A.
Score = (passes + 0.5 × partials) / applicable checks, shown overall and per category.
"100% LLM readable" means every applicable check passes. Mark a check N/A only with
a reason (e.g. G4 on a site with no videos).

**Severity guide**
- **Critical:** an LLM can't get the content at all, or gets wrong facts about the author.
- **High:** content is reachable but key facts are missing, ambiguous or hard to attribute.
- **Medium:** metadata or structure gaps that reduce accuracy or discoverability.
- **Low:** polish and hygiene.

Who reads the site: recruiter pipelines that fetch a URL and summarise it; AI search
(ChatGPT search, Perplexity, Claude, Google AI Overviews); agents following links. Almost
none of them run JavaScript, look at images, or wait for animations. Many truncate long
HTML before stripping tags. Assume a model that reads raw HTML once, top to bottom.

---

## A. Access and crawlability

**A1 Content is in the initial HTML** (Critical, auto/partial)
- Why: most LLM fetchers don't execute JS. A client-rendered page looks empty to them.
- Detect: bot `likely_client_rendered`, low `text_chars` on content pages; static: SPA with `<div id="root">` and no SSR/SSG/prerender.
- Fix: enable SSG/SSR/prerendering for the stack (see stacks.md). If impossible, ship llms-full.txt and a `<noscript>` summary as a stopgap and say it's a stopgap.

**A2 Text isn't hidden behind interaction** (High, auto)
- Why: content that only appears in modals, hover cards, tabs loaded on click or carousels never reaches the HTML.
- Detect: static: content rendered conditionally on state (`isOpen && …`), fetched on click; bot: compare page text with the source content.
- Fix: render it in the DOM (visually collapsed is fine), or give it its own page/section.

**A3 robots.txt exists and doesn't block AI crawlers unintentionally** (High, auto, ask first)
- Why: GPTBot, ClaudeBot, PerplexityBot, Google-Extended and CCBot obey robots.txt. A stray `Disallow: /` hides everything.
- Detect: bot `site_files./robots.txt.ai_bots`.
- Fix: add robots via the stack's mechanism. **If the author blocked AI bots on purpose, respect that and only report it.** Always confirm before loosening rules.

**A4 sitemap.xml lists every public page** (Medium, auto)
- Why: agents find pages by links; a sitemap guarantees they find case studies and posts that are only linked deep in the site.
- Detect: bot `site_files./sitemap.xml`; compare `urls` with the route inventory.
- Fix: generate from the route/content source, not by hand. Reference it in robots.txt.

**A5 Key pages return 200** (Critical, auto)
- Detect: bot `errors`; static: broken internal links.
- Exclude failures caused by the local environment (missing env vars, unseeded database, auth-only services). Read the server log; if that's the cause, mark Pass/unknown, note it under Caveats and verify on the live site.
- Routes that 404 on purpose (removed pages with redirects) aren't failures; linked pages that 404 are.
- Fix: repair links/routes; add redirects for moved URLs.

**A6 Host redirects are permanent and there's one canonical host** (Medium, platform/auto)
- Why: 302/307 tells crawlers the move is temporary, so apex vs www (or old domain) can be treated as separate sites.
- Detect: bot `home_redirects`, `non_permanent_redirects`.
- Fix: hosting/DNS setting (Vercel: Domains → Edit → 308; Netlify: `_redirects` with `301!`; Cloudflare: redirect rule 301). Code-level redirects in the framework config if that's where they live.

**A7 Unfinished, test and placeholder pages are noindexed or removed** (High, auto)
- Why: a crawler that finds a `/sandbox`, `/test` or lorem-ipsum page will credit it to the author.
- Detect: static: playground/sandbox/test/draft routes, lorem, fake links; bot `placeholder_text_hits`, `fake_links`.
- Fix: delete, or add `noindex` (meta robots) **and** exclude from sitemap and llms files. Ask before deleting.

**A8 Primary navigation is in the initial HTML** (High, auto)
- Why: crawlers discover pages by following links. A navbar or menu that only renders after hydration (`if (!mounted) return null`, `useEffect`-gated, opened by click and fetched lazily) leaves the home page linking to almost nothing, so whole sections are found only via the sitemap, or never.
- Detect: bot `pages_not_linked_from_home` / `home_internal_links` (run with `--sitemap` or pass all routes); static: the nav component's render guards.
- Fix: render the nav links on the server (animate on the client if needed), or at minimum a server-rendered link list (footer/`<noscript>`) to every main section.

## B. Machine-readable summaries

**B1 /llms.txt exists and follows llmstxt.org** (High, auto)
- Why: one small markdown file that tells a model who this is and where everything lives.
- Format: `# Name` → `> one-line summary` → short context → `## Section` lists of `- [Title](absolute URL): one-line description` → optional `## Optional` section.
- Detect: bot `site_files./llms.txt` (status 200, `starts_with_h1`, not HTML).
- Fix: generate from content sources at build time (stacks.md). Absolute URLs on the canonical host.

**B2 /llms-full.txt (or markdown mirrors) has the full content in one fetch** (High, auto)
- Why: lets a screener read bio, experience and every case study in one request, without HTML noise or truncation.
- Content: identity block, about/bio, experience (role, company, dates, what they did, collaborators), every case study/post as markdown with images as `[Image: alt]` lines, smaller items (lab/projects) with one-line descriptions.
- Fix: generate from the same data the pages render. Keep it under ~150 KB; past that, link per-section markdown files.

**B3 Generated, not hand-copied** (Medium, auto)
- Why: hand-written copies drift from the site within weeks, and stale facts are worse than none.
- Fix: one builder function reading the content sources; static file only when the stack has no build (plain HTML, site builders), and say so.

## C. Identity and structured data

**C1 Person (or Organization) JSON-LD on every page** (High, auto + input)
- Fields: `name`, `url`, `image`, `jobTitle`, `worksFor`, `description`, `sameAs` (LinkedIn, GitHub, X, Dribbble…), `knowsAbout` (skills), optional `address.addressLocality`, `email`.
- Detect: bot `jsonld_types`, `pages_without_jsonld`.
- Fix: one identity source of truth (e.g. `site.config`) feeding JSON-LD, metadata and llms files. Use a stable `@id` (`https://site/#person`) and reference it from other nodes.

**C2 Per-page structured data matches page type** (Medium, auto)
- Case study → `CreativeWork` (name, description, url, author @id, sourceOrganization); post → `BlogPosting`/`Article` (headline, datePublished, author); product → `Product`; company → `Organization`; docs → `TechArticle`.

**C3 The same facts everywhere** (High, input)
- Why: if the home page says "chief pixel pusher", the about page says "Designer" and the meta says "Senior Product Designer", a model has to guess.
- Detect: static: grep title/role/company/years strings across pages, metadata, OG images, résumé.
- Fix: ask the author for the canonical wording, then apply it everywhere, including OG image templates and the identity source.

**C4 Valid JSON-LD** (Medium, auto)
- Detect: bot `jsonld_parse_errors`. Escape `<` in inline JSON.

## D. Page metadata

**D1 Unique `<title>` that names the person/brand** (Medium, auto)
- Why: pipelines that store or cite pages by title lose "whose page this is" with bare titles like "Work".
- Detect: bot `title`, `duplicate_titles`.
- Fix: a title template (`%s · Name`); a full title on the home page.

**D2 Meta description on every indexable page** (Medium, auto)
- Fix: reuse the page's own intro copy where it exists; for case studies, the one-line summary; for posts, the first paragraph trimmed to ~160 characters. Don't write new marketing copy.

**D3 Canonical URL on every indexable page** (Medium, auto)
- Fix: absolute canonical on the host that actually serves 200 (follow redirects to find it).

**D4 OG/Twitter tags** (Low, auto): `og:title`, `og:description`, `og:image`, `twitter:card`.

**D5 `<html lang>` set** (Low, auto)

## E. Structure and semantics

**E1 Exactly one h1 per page** (Medium, auto). Detect: bot `pages_without_single_h1`.

**E2 No skipped heading levels**, and section titles are real headings rather than styled divs (Low, auto). Detect: bot `heading_level_skipped`, `headings`.

**E3 Landmarks** (`main`, `nav`, `article`, `header`, `footer`) (Low, auto).

**E4 Descriptive link text and labelled icon-only links** (Medium, auto)
- Why: "click here" or an icon with no label gives the model nothing to follow.
- Fix: `aria-label` on icon-only links, real text where possible.

**E5 Key facts are text, not pixels** (High, input/auto)
- Why: role, results and process baked into images, Figma embeds, canvas or video are invisible.
- Fix: add the facts as text near the visual; at minimum a descriptive alt/caption.

## F. Content substance (the checks depend on site type; see site-types.md)

These are scored per site type. For portfolios:

- **F1 Role and ownership** stated per project ("I led…", "my role: …"), not only "we". (High, input)
- **F2 Context:** company, team, collaborators, duration, platform. (High, input)
- **F3 Problem → process → decisions** with reasons. (Medium, usually already present)
- **F4 Outcomes:** metrics, or a qualitative result, or shipped/not shipped. (High, input; the biggest gap on most portfolios)
- **F5 Unambiguous dates:** project period, not just a publish date with no label. (High, input)
- **F6 Explicit skills/tools/domains**, matchable against job descriptions. (Medium, input)
- **F7 Current role, location/timezone, availability, contact.** (Medium, input)
- **F8 No typos in titles/headings; no copy-pasted leftovers in data files.** (Low, auto. Fix obvious typos only and list each one.)
- **F9 No placeholder, lorem or fake content anywhere public.** (Critical if present, auto/ask)

## G. Media

**G1 Descriptive alt text on every content image** (High, auto)
- Why: the design work in a portfolio is mostly images; without alt text, a text-only reader sees nothing.
- Detect: bot `images_missing_alt`, and `images_empty_alt_suspect`: empty alt on a content image is usually **missing**, not decorative, because many image components default `alt` to `""`. Confirm in the source by counting content/data entries with no alt field.
- Fix: **open each image** (Read tool; downscale first with `sips`/ffmpeg/ImageMagick if large) and describe what it shows and why it's there: "Checkout step 2: delivery options with prices", not "image1". Decorative images get `alt=""` plus `aria-hidden` or `role="presentation"`. Never guess from filenames.

**G2 Unique alt text**: no identical alt on different images. (Low, auto)

**G3 Videos described** (Medium, auto)
- Fix: `aria-label`/caption describing what the video demonstrates; extract a frame (ffmpeg `-ss 2 -frames:v 1`) to see it. Long talks/demos: transcript or summary text.

**G4 Résumé available as text** (Medium, auto/input)
- Why: image-only or scanned PDFs are unreadable; an HTML résumé or text-based PDF is ideal.
- Detect: find `*.pdf` and check for extractable text (`pdftotext` if present, or Read).

**G5 No image-only case studies or posts** (High, input). A page that's only screenshots needs at least a written summary.

## H. Payload and efficiency

**H1 Content-to-HTML ratio is reasonable** (Medium, auto/partial)
- Why: fetchers often cap at 100–500 KB of raw HTML before stripping tags; a very large page with only a few KB of real text risks being cut off before the content.
- bot_view only flags pages over 100 KB; a low ratio on a small page is harmless.
- Detect: bot `text_ratio_pct` < 2%, `html_bytes` > 300 KB.
- Fix options: drop large inline blur/base64 placeholders, avoid serialising whole content twice (hydration payloads), lazy-load non-critical components. Since this often isn't fully fixable, B2 (llms-full) is the mitigation. Mark Partial with the mitigation noted.

**H2 Inline base64 bloat** (Low, auto). Detect: bot `inline_base64_bytes`.

## I. Hygiene

**I1 No broken or fake links** (Medium, auto). Detect: bot `fake_links`; static: `href="#"`, google.com/example.com placeholders.
**I2 Internal links use one host** (Low, auto). Absolute links should match the canonical host.
**I3 No duplicate pages** under different URLs without a canonical (Low, auto). Includes test/sandbox copies of real pages (e.g. a draft copy of a case study): noindex or remove them.
**I4 "Last updated" or dates aren't misleading** (Low, input).

---

## Score sheet

Copy into your working notes and fill in as you go. bot_view's `score_hints` pre-fills the rows marked •; confirm each one.

| Cat | Checks | Pass | Partial | Fail | N/A |
|---|---|---|---|---|---|
| A Access | A1• A2 A3• A4• A5• A6• A7 A8• | | | | |
| B Summaries | B1• B2• B3 | | | | |
| C Identity | C1• C2 C3 C4• | | | | |
| D Metadata | D1• D2• D3• D4 D5• | | | | |
| E Structure | E1• E2• E3 E4 E5 | | | | |
| F Content | F1–F9 (per site type) | | | | |
| G Media | G1• G2 G3• G4 G5 | | | | |
| H Payload | H1• H2 | | | | |
| I Hygiene | I1• I2 I3 I4 | | | | |
| **Total** | | | | | |

Score = (Pass + 0.5 × Partial) / (Total − N/A).

## Quick map: bot_view.py field → checks
| Field | Checks |
|---|---|
| `likely_client_rendered`, `text_chars` | A1 |
| `site_files./robots.txt.ai_bots` | A3 |
| `home_internal_links`, `pages_not_linked_from_home` | A8 |
| `site_files./sitemap.xml` | A4 |
| `errors`, `status` | A5 |
| `home_redirects`, `non_permanent_redirects` | A6 |
| `noindexed_pages`, `placeholder_text_hits`, `fake_links` | A7, F9, I1 |
| `site_files./llms.txt`, `/llms-full.txt` | B1, B2 |
| `jsonld_types`, `jsonld_parse_errors` | C1, C2, C4 |
| `title`, `duplicate_titles` | D1 |
| `meta_description`, `canonical`, `og_*`, `lang` | D2–D5 |
| `h1`, `headings`, `heading_level_skipped`, `landmarks` | E1–E3 |
| `images_missing_alt`, `images_empty_alt_suspect`, `videos_unlabelled` | G1–G3 |
| `score_hints` | pre-filled verdicts for the • checks |
| `text_ratio_pct`, `html_bytes`, `inline_base64_*` | H1, H2 |
