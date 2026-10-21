# Site types: what "good content" means for each

Category F in checklist.md depends on what the site is for. Classify the site in
Phase 0 from its pages and copy, and say which type you picked in the report. A site
can be a mix (a portfolio with a blog); score each part against its own type.

The question behind every check: **if a model had only this site, could it answer
the questions its reader is likely to ask, correctly and with evidence?**

---

## Portfolio (designers, engineers, writers, researchers, artists)

Likely reader: a recruiter's screening pipeline, a hiring manager's assistant, AI search.
Questions it will try to answer:
- Who is this, what's their current title, where do they work, how senior are they?
- What did *they* personally do on each project, compared with the team?
- What was the impact? Is there evidence?
- Which skills/tools match the job description?
- How long, when, at which company? Are the dates consistent with the experience page?
- Where are they based, and are they available? How do I contact them?

Checks F1–F9 in checklist.md, plus:
- Each case study opens with a short **facts line**: Role · Team · Duration · Platform · Status (shipped / concept / ongoing). Offer to add it, but the values must come from the author.
- Experience entries include role, company, start–end dates and 1–3 lines of what they did.
- Skills appear in plain words somewhere crawlable (bio, about, footer, JSON-LD `knowsAbout`).
- Side projects/experiments get one line saying what each is and what it was built with.
- Writing/notes are a strength: they show thinking and voice. Make sure they're in llms-full.

Common gaps to look for (use this list while reading in Phase 1, not only to classify):
- No outcomes ("we saw an increase").
- Publish dates mistaken for project dates. **Cross-check:** a case study dated after the job that produced it ended (compare with the experience page) means the date is a publish date or wrong.
- A title that differs across pages, or a playful title that isn't matchable ("chief pixel pusher").
- "We" everywhere, with no statement of what the author owned.
- Case studies that are mostly screenshots.
- Intern vs full-time work: check whether each case study says what role the author had at the time. Either is fine, but a screener should be able to tell.
- Leftovers in data files: a subtitle copied from another project, an unused field with wrong text.

## Company / product / startup site

Likely reader: AI search answering "what does X do / how much / who is it for / alternatives".
- What the product does, in one plain sentence near the top (not only a slogan).
- Who it's for, key features, pricing (or "contact sales" stated explicitly), integrations.
- Company facts: founded, location, team, contact, legal name. `Organization` JSON-LD with `sameAs`, `logo`.
- Product JSON-LD (`SoftwareApplication`/`Product`) with offers when pricing is public.
- FAQ answering real questions in text (`FAQPage` JSON-LD where it's genuinely an FAQ).
- Docs/changelog linked and crawlable; comparison and use-case pages are high value.
- Testimonials/case studies attributed (name, company) in text, not only logos.

## Blog / writing / newsletter

Likely reader: AI search citing articles; readers' assistants summarising.
- Each post: title, author, `datePublished`/`dateModified`, a summary or first paragraph that states the point.
- `BlogPosting`/`Article` JSON-LD; author page with `Person` JSON-LD.
- Tags/categories as crawlable pages; an RSS/Atom feed linked in `<head>`.
- Code blocks as text (not screenshots); images with alt text.
- llms.txt lists posts with one-line summaries; llms-full can hold the full text if it's under ~150 KB, otherwise only the newest/most important posts plus links.

## Docs / developer site

Likely reader: coding assistants and agents.
- Every page has a clear title and a one-sentence purpose.
- Code samples as text, with language tags; API reference in text, not only interactive explorers.
- llms.txt organised by section; per-page markdown versions (`/page.md`) are very valuable.
- Version clearly stated; deprecated pages marked.
- `TechArticle` JSON-LD optional; sitemap essential.

## Store / e-commerce

Likely reader: shopping assistants.
- Product name, price, currency, availability, variants, shipping and returns in text.
- `Product` + `Offer` JSON-LD with `price`, `priceCurrency`, `availability`; `AggregateRating` only if real reviews exist.
- Policies (shipping, returns, contact) on crawlable pages.
- Don't block product pages in robots.txt; facets/filters can be noindexed.

## Personal / link-in-bio / event / other

Fall back to: who/what is this, the key facts a stranger would ask about, how to contact,
and whether all of it is in crawlable text. Use checklist categories A–E and G–I as is,
and write the F checks as 3–6 questions specific to the site's purpose. List those
questions in the report.
