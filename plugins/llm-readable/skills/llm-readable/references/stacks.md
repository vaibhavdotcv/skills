# Stack recipes

Where each fix goes, per framework. **Framework APIs change between versions.** Before
writing code, check the installed version (`package.json`, lockfile) and read the docs
that ship with it (e.g. `node_modules/<framework>/docs`, `node_modules/next/dist/docs/`),
plus any AGENTS.md / CLAUDE.md in the repo. Where this file and the installed docs
disagree, the installed docs win.

General pattern for every stack (adapt the file names):
1. **One identity source**, e.g. `site.config.(js|ts)`, `src/data/site.json`, `_data/site.yml`, `config.toml [params]`. It holds name, title, employer, summary, links, skills and the canonical `SITE_URL` (the host that returns 200 after redirects). Everything else imports it.
2. **One content-flattening helper** that turns the site's content (markdown, MDX, data files, CMS responses) into plain text/markdown. It's used by meta descriptions, JSON-LD, the sitemap and the llms files. Reuse what exists (RSS builders, search-index builders and content collections often already do this).
3. **llms.txt / llms-full.txt built from that helper** at build time: a route/endpoint marked static, or a prebuild script that writes into the public/static folder.
4. Exclude unfinished pages from the sitemap and llms files, and noindex them.

If a build script is the only option, wire it into the existing build (`prebuild` in package.json, a Hugo/Jekyll hook, a CI step) rather than leaving a manual step.

---

## Next.js (App Router: `app/`)
- Metadata: `export const metadata` / `generateMetadata` in `layout`/`page`. Root layout: `metadataBase`, `title: { default, template: "%s · Name" }`, `description`. Home: `title: { absolute: … }` so the template doesn't double the name. Per page: `description`, `alternates: { canonical: "/path" }`.
- noindex: `robots: { index: false, follow: false }` in a segment's `layout` metadata (covers the whole subtree; `layout` can be a server component that only returns `children`).
- Sitemap: `app/sitemap.(js|ts)` default export returning `[{ url, lastModified, priority }]`. Robots: `app/robots.(js|ts)`.
- llms: route handlers `app/llms.txt/route.(js|ts)` and `app/llms-full.txt/route.(js|ts)` with `export const dynamic = "force-static"` and `GET` returning `new Response(text, { headers: { "Content-Type": "text/plain; charset=utf-8" } })`. Don't import client components (`"use client"`) into them; split data from components if needed.
- JSON-LD: `<script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(data).replace(/</g, "\\u003c") }} />` in the root layout (Person) and in pages (CreativeWork/BlogPosting).
- Alt text: `next/image` `alt`; content data objects usually hold `alt` fields.
- Check: `next build` output lists `/robots.txt`, `/sitemap.xml`, `/llms.txt` as static; built HTML lives in `.next/server/app/*.html` for inspection.

## Next.js (Pages Router: `pages/`)
- Metadata via `next/head` per page, or a shared `<Seo>` component. Title template by hand.
- Sitemap/robots: `pages/sitemap.xml.(js|ts)` with `getServerSideProps` writing XML, or a prebuild script into `public/`. `next-sitemap` if it's already a dependency.
- llms: prebuild script writing `public/llms.txt`, or an API route rewritten from `/llms.txt` in `next.config` `rewrites`.
- JSON-LD in `<Head>` the same way as above.

## Astro
- Metadata: a `<BaseHead>`/`<SEO>` component in the layout; props per page. Canonical: `new URL(Astro.url.pathname, Astro.site)`.
- `site` in `astro.config.*` must be set (canonical host).
- Sitemap: `@astrojs/sitemap` integration (filter out unfinished pages). Robots: `src/pages/robots.txt.ts` endpoint or `public/robots.txt`.
- llms: `src/pages/llms.txt.ts` endpoint (`export const GET = () => new Response(text)`; static by default in SSG). Read content with `getCollection()`.
- JSON-LD: `<script type="application/ld+json" set:html={JSON.stringify(data)} />`.

## Nuxt
- Metadata: `useHead` / `useSeoMeta` per page; app-wide in `app.vue` or `nuxt.config` `app.head`. `@nuxtjs/seo` (or `@nuxtjs/sitemap`, `@nuxtjs/robots`, `nuxt-schema-org`) if already installed; otherwise server routes.
- llms: `server/routes/llms.txt.ts` with `defineEventHandler`, plus `nitro.prerender.routes: ['/llms.txt', '/llms-full.txt']` for static output.
- Make sure pages are SSR/SSG (`ssr: true`, or `nuxi generate`), not SPA mode.

## SvelteKit
- Metadata: `<svelte:head>` in `+layout.svelte` / `+page.svelte`; data from `+page.(js|ts)` `load`.
- Prerender: `export const prerender = true` in the root `+layout.(js|ts)` for static sites.
- Endpoints: `src/routes/sitemap.xml/+server.(js|ts)`, `src/routes/robots.txt/+server.(js|ts)`, `src/routes/llms.txt/+server.(js|ts)` with `export const prerender = true`.

## Remix / React Router v7 (framework mode)
- Metadata: `meta` export per route (`[{ title }, { name: "description", content }, { tagName: "link", rel: "canonical", href }]`).
- Resource routes for files: `app/routes/llms[.]txt.(ts|tsx)` (`loader` returning `new Response`), same for `sitemap[.]xml`, `robots[.]txt`. Use prerendering if the app is configured for it.

## Gatsby
- Metadata: the `Head` export API (or `react-helmet` in older sites).
- Sitemap: `gatsby-plugin-sitemap`; robots: `gatsby-plugin-robots-txt` or `static/robots.txt`.
- llms: `onPostBuild` in `gatsby-node.js` querying GraphQL and writing `public/llms.txt`.

## Vite / CRA single-page apps (React, Vue, Svelte without SSR)
- **A1 fails by default**: the HTML is an empty shell. Options, best first:
  1. Prerender the routes at build time (`vite-plugin-prerender`/`vite-ssg` for Vue, `react-snap`-style tools, or framework migration). Ask before adding dependencies.
  2. If prerendering isn't acceptable now: put a real `<noscript>` and a static summary block in `index.html`, and rely on llms.txt / llms-full.txt. Report A1 as **Partial** with this caveat.
- Metadata per route: `react-helmet-async` / `@unhead/vue` only helps crawlers that run JS. Set good defaults in `index.html`.
- Sitemap/robots/llms: a Node script in `scripts/` run from `prebuild`, writing into `public/`. Import the same data modules the app uses (use `tsx`/`node --experimental-strip-types` if the data is TS).

## Hugo
- Metadata: `layouts/partials/head.html` (or the theme's partial: override it, don't edit the theme). `.Description`, `.Summary`, `.Permalink`.
- Sitemap is built in (`sitemap.xml`); set `baseURL`. Robots: `enableRobotsTXT = true` + `layouts/robots.txt`.
- llms: a custom output format. Add `[outputFormats.llms] mediaType = "text/plain" baseName = "llms" isPlainText = true` and `[outputs] home = ["HTML", "RSS", "llms"]`, then `layouts/index.llms.txt` ranging over `.Site.RegularPages` (`.Plain` for full text in llms-full).
- JSON-LD: a partial in head using `jsonify`.

## Jekyll
- Metadata: `jekyll-seo-tag` if present (`{% seo %}`); otherwise `_includes/head.html`.
- Sitemap: `jekyll-sitemap`. Robots: `robots.txt` with front matter.
- llms: `llms.txt` at the root with front matter (`layout: null`, `permalink: /llms.txt`) and Liquid looping over `site.posts` / collections (`{{ post.content | strip_html }}` for full text).

## Eleventy (11ty)
- Metadata in the base layout using front matter data; global data in `_data/site.js`.
- Sitemap/robots/llms: templates with `permalink: /llms.txt` and `eleventyExcludeFromCollections: true`, looping over `collections.all`.

## Plain HTML / static folder
- Edit each page's `<head>`: title, description, canonical, OG, JSON-LD.
- Write `robots.txt`, `sitemap.xml`, `llms.txt`, `llms-full.txt` as static files. Say clearly in the change log that these are **hand-maintained** and must be updated with the content (B3 = Partial). Offer a tiny generator script if there are more than ~10 pages.

## WordPress (theme or child theme in repo)
- Prefer an SEO plugin already installed (Yoast/Rank Math handle titles, descriptions, sitemaps, schema). Don't add plugins without asking.
- Theme-level: `functions.php` hooks (`wp_head` for JSON-LD, `document_title_parts`). llms.txt: a rewrite rule + template, or a plugin if the author agrees.
- Most WordPress fixes are content edits in wp-admin. List them as `platform` steps.

## Site builders: Framer, Webflow, Wix, Squarespace, Notion-based sites, Carrd
- There's usually no repo to edit. Run the audit from the live URL (bot_view.py) and any exported code. Then give paste-ready output:
  - Page settings: title and description text per page, written out.
  - Custom code → head: the JSON-LD `<script>` block, ready to paste.
  - llms.txt / robots.txt contents as text, plus where to put them (Framer: Site settings → robots.txt is editable; for llms.txt, a page or redirect to a hosted file. Webflow: Site settings → SEO → robots.txt; host llms.txt externally or via a reverse proxy. Wix/Squarespace: robots editing is limited; host llms.txt on a subdomain and link it). Platform UIs change, so tell the author to look for the named setting rather than promising exact click paths.
  - Alt text per image, listed by page and image.
- If the author exported the site to code (e.g. a Framer-to-code conversion), treat that as plain HTML.

## Headless CMS content (Contentful, Sanity, Notion API, Strapi…)
- The fix is often in the **content** (alt text fields, descriptions, role/outcome fields), not the code. Code changes: make the templates *use* those fields and include them in llms output. Content changes: list them per entry as `platform` steps, or write them via the CMS API only if the author explicitly asks and credentials are already configured.
