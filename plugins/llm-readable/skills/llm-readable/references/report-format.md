# Report formats

Three outputs, in this order: the **audit report** (Phase 3), the **next steps**
(Phase 4) and, after changes, the **change log** (Phase 8). Write in plain language
for the site's author, who may not be technical. Lead with what matters most and keep
evidence concrete: file:line links, URLs, measured numbers.

If the report is long (it usually is), also save it as `LLM-READABILITY.md` in the
project root **only if the author agrees**. Otherwise keep it in chat.

---

## 1. Audit report

```markdown
# LLM-readability audit: <site name>

**Site:** <canonical URL> · **Stack:** <framework + version> · **Type:** <portfolio / company / blog / …>
**How I checked:** read <N> source files across <M> routes; fetched <K> pages as GPTBot (no JavaScript) <from live / local build / not reachable>.
**Caveats:** <local-only artefacts (e.g. a page that 500s because env vars aren't set locally), parts not checked and why, or "none">.

## Score: <XX>% (<passed>/<applicable> checks)
| Category | Score | Biggest issue |
|---|---|---|
| A. Access | 5/7 | Apex redirects with a temporary 307 |
| B. Machine summaries | 0/3 | No llms.txt |
| … | | |

## What's working for you
1. **<Strength, one line>** (<check IDs>)
   <Evidence: what you saw, with file:line or URL + number.>
   *Why it helps:* <one or two sentences on how an LLM reader benefits.>

## What's holding you back
Ordered by severity, then by how many readers it affects.

1. **<Problem, one line>** · <Critical/High/Medium/Low> · <I can fix / Needs your input / Outside the repo> (<check IDs>)
   <Evidence.>
   *Why it hurts:* <the concrete consequence, e.g. "a screener scoring 'measurable impact' has nothing to cite".>
```

Rules:
- Every claim carries evidence. "Pages lack descriptions" → name the pages or give the count from bot_view.
- Separate *observed* from *inferred* ("The 600 KB pricing page **may** be cut off by fetchers that cap at ~100–500 KB").
- Content problems (F checks) name the exact sentence or field. Quote at most a short phrase.
- Don't pad the strengths list. 4–10 real items beat 20 trivial ones.

## 2. Next steps

```markdown
## Next steps to reach 100%

### I can do these now (<n>)
| # | Fix | Checks | Files I'd touch | Visible change? | Deletes anything? |
|---|---|---|---|---|---|
| 1 | Generate /llms.txt and /llms-full.txt from your content | B1–B3 | new: lib/llms.ts, app/llms.txt/route.ts | No | No |
| 2 | Write alt text for 42 images (after looking at each one) | G1 | content/work/*.mdx | No (screen readers only) | No |
| 3 | Remove the placeholder "Projects" list | F9, I1 | src/pages/projects.astro | Yes | **Yes, needs your OK** |

### Needs your input (<n>)
| # | What I need | Why | Where it goes |
|---|---|---|---|
| 1 | Outcome of each case study: a metric, a rough figure or "shipped to X users" | F4 | First section of each case study |
| 2 | Your canonical job title ("Product Designer"?) | C3 | Home, bio, meta, JSON-LD |

### Outside the repo (<n>)
| # | Where | Exact steps |
|---|---|---|
| 1 | Vercel → Project → Settings → Domains | Edit `example.com` → Redirect to `www.example.com` → **308 Permanent** |

**After all of this, the expected score is <YY>%.** Anything that would still fail is listed with the reason.
```

Then ask for approval (Phase 5).

## 3. Change log

```markdown
# What I changed

**Score:** <XX>% → <YY>% · **Build:** <passed/failed + command> · **Re-checked with:** bot_view.py on <local build / preview URL>

## Problem → change
| # | Problem (from the audit) | Status | What changed | Files |
|---|---|---|---|---|
| 1 | No llms.txt / llms-full.txt | ✅ Fixed | Both are generated from the content files at build time | `lib/llms.ts`, `app/llms.txt/route.ts` (new) |
| 2 | 42 images with no alt text | ✅ Fixed | Wrote alt text after viewing each image | `content/work/*.mdx` |
| 3 | Case studies have no outcomes | ⏸ Needs you | Placeholders were **not** added; here's what to write | — |
| 4 | Apex redirect is 307 | ↗ Outside repo | Steps above | — |
| 5 | /sandbox demo pages crawlable | ✅ Fixed | noindex + excluded from sitemap and llms | `src/pages/sandbox/_layout.astro` |

## New files
- `path`: one line on what it is

## Things to review
- <Anything written in the author's name: alt text, descriptions, one-liners. Point to where they are so the author can skim them.>
- <Any judgement call, e.g. "picked www as the canonical host because the apex redirects to it".>

## Still open
- <Each remaining failing check, with what would close it.>

Nothing has been committed or deployed.
```

Status legend: ✅ Fixed · 🟡 Partly fixed (say what's left) · ⏸ Needs you · ↗ Outside repo · ⏭ Skipped by choice (say whose choice).
Every "Holding you back" item from the audit appears exactly once in the table.
