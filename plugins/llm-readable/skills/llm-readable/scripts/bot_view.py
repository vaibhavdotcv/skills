#!/usr/bin/env python3
"""
bot_view.py: see a website the way an AI crawler / LLM fetcher sees it.

No JavaScript is executed. Pages are fetched with a crawler User-Agent and
the raw HTML is measured: what text is there, what metadata is there, how
much of the payload is actual content. Python 3.8+ standard library only.

Usage:
  python3 bot_view.py https://example.com
  python3 bot_view.py https://example.com /about /work/case-study
  python3 bot_view.py https://example.com --sitemap 30
  python3 bot_view.py http://localhost:3000 --ua claudebot --pretty

Output is JSON on stdout (summary + per-page details).
"""

import argparse
import json
import re
import sys
import time
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

USER_AGENTS = {
    "gptbot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "claudebot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)",
    "perplexitybot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)",
    "googlebot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "browser": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
}

# Crawlers whose robots.txt access matters for LLM visibility.
AI_BOTS = [
    "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot",
    "anthropic-ai", "PerplexityBot", "Perplexity-User", "Google-Extended", "CCBot",
    "Applebot-Extended", "Bytespider", "meta-externalagent",
]

LOW_RATIO_MIN_BYTES = 100_000

FAKE_LINK_RE = re.compile(r"^(https?://(www\.)?(google|example|test|placeholder)\.(com|org)/?$|#$|javascript:void)", re.I)
PLACEHOLDER_TEXT_RE = re.compile(r"\b(lorem ipsum|dolor sit amet|placeholder|coming soon|todo|tbd|your name here)\b", re.I)


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_opener = build_opener(_NoRedirect)


def fetch(url, ua, timeout=20, max_redirects=8):
    """GET a URL, following redirects by hand so every hop's status is recorded."""
    chain = []
    current = url
    for _ in range(max_redirects + 1):
        req = Request(current, headers={"User-Agent": ua, "Accept": "text/html,text/plain,application/xml;q=0.9,*/*;q=0.8"})
        start = time.time()
        try:
            resp = _opener.open(req, timeout=timeout)
            body = resp.read()
            chain.append({"url": current, "status": resp.status})
            return {
                "final_url": current,
                "status": resp.status,
                "chain": chain,
                "headers": {k.lower(): v for k, v in resp.headers.items()},
                "body": body,
                "ms": int((time.time() - start) * 1000),
            }
        except HTTPError as e:
            location = e.headers.get("Location") if e.headers else None
            chain.append({"url": current, "status": e.code})
            if 300 <= e.code < 400 and location:
                current = urljoin(current, location)
                continue
            body = e.read() if hasattr(e, "read") else b""
            return {"final_url": current, "status": e.code, "chain": chain,
                    "headers": {k.lower(): v for k, v in (e.headers or {}).items()}, "body": body, "ms": None}
        except (URLError, OSError, ValueError) as e:
            chain.append({"url": current, "error": str(getattr(e, "reason", e))})
            return {"final_url": current, "status": None, "chain": chain, "headers": {}, "body": b"", "error": str(getattr(e, "reason", e))}
    return {"final_url": current, "status": None, "chain": chain, "headers": {}, "body": b"", "error": "too many redirects"}


def decode(body, headers):
    charset = "utf-8"
    ctype = headers.get("content-type", "")
    m = re.search(r"charset=([\w-]+)", ctype)
    if m:
        charset = m.group(1)
    try:
        return body.decode(charset, errors="replace")
    except LookupError:
        return body.decode("utf-8", errors="replace")


class PageParser(HTMLParser):
    SKIP = {"script", "style", "noscript", "template", "svg", "head"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.title = None
        self._in_title = False
        self.meta = {}
        self.links = []
        self.canonical = None
        self.headings = []
        self._heading = None
        self.images = []
        self.videos = 0
        self.videos_labelled = 0
        self.jsonld_raw = []
        self._in_jsonld = False
        self._jsonld_buf = []
        self.scripts = 0
        self._skip_depth = 0
        self.text_parts = []
        self.landmarks = set()
        self._content_depth = 0  # >0 while inside <main> or <article>

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "html":
            self.lang = a.get("lang") or None
        elif tag == "title" and self.title is None:
            self._in_title = True
        elif tag == "meta":
            key = (a.get("name") or a.get("property") or "").lower()
            if key:
                self.meta[key] = a.get("content", "")
        elif tag == "link" and "canonical" in a.get("rel", "").lower().split():
            self.canonical = a.get("href")
        elif tag == "a":
            self.links.append(a.get("href", ""))
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._heading = [int(tag[1]), []]
        elif tag == "img":
            self.images.append({
                "src": a.get("src", "")[:120],
                "alt": a.get("alt") if "alt" in a else None,
                # alt="" is only truly decorative when the page also says so
                "decorative": a.get("aria-hidden") == "true" or a.get("role") in ("presentation", "none"),
                "in_content": self._content_depth > 0,
            })
        elif tag == "video":
            self.videos += 1
            if a.get("aria-label") or a.get("title") or a.get("aria-describedby"):
                self.videos_labelled += 1
        elif tag in ("main", "nav", "header", "footer", "article"):
            self.landmarks.add(tag)
            if tag in ("main", "article"):
                self._content_depth += 1
        if tag == "script":
            self.scripts += 1
            if "ld+json" in a.get("type", "").lower():
                self._in_jsonld = True
                self._jsonld_buf = []
        if tag in self.SKIP:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._heading:
            level, parts = self._heading
            self.headings.append((level, " ".join("".join(parts).split())))
            self._heading = None
        if tag == "script" and self._in_jsonld:
            self.jsonld_raw.append("".join(self._jsonld_buf))
            self._in_jsonld = False
        if tag in self.SKIP and self._skip_depth:
            self._skip_depth -= 1
        if tag in ("main", "article") and self._content_depth:
            self._content_depth -= 1

    def handle_data(self, data):
        if self._in_title:
            self.title = (self.title or "") + data
        if self._in_jsonld:
            self._jsonld_buf.append(data)
        if self._heading is not None:
            self._heading[1].append(data)
        if not self._skip_depth:
            self.text_parts.append(data)


def jsonld_types(raw_blocks):
    types, errors = [], 0

    def walk(node):
        if isinstance(node, dict):
            t = node.get("@type")
            if t:
                types.extend(t if isinstance(t, list) else [t])
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    for raw in raw_blocks:
        try:
            walk(json.loads(raw))
        except ValueError:
            errors += 1
    return types, errors


def analyse_page(url, ua):
    res = fetch(url, ua)
    page = {"url": url, "status": res["status"], "final_url": res["final_url"]}
    if len(res["chain"]) > 1:
        page["redirects"] = res["chain"]
    if res.get("error"):
        page["error"] = res["error"]
        return page

    html = decode(res["body"], res["headers"])
    p = PageParser()
    try:
        p.feed(html)
    except Exception as e:  # malformed HTML should not kill the run
        page["parse_error"] = str(e)

    text = " ".join(" ".join(p.text_parts).split())
    types, ld_errors = jsonld_types(p.jsonld_raw)
    base64 = re.findall(r"data:[\w/+.-]+;base64,[A-Za-z0-9+/=]+", html)
    h_levels = [lvl for lvl, _ in p.headings]
    skipped = any(b - a > 1 for a, b in zip(h_levels, h_levels[1:]))
    imgs_no_alt = [i["src"] for i in p.images if i["alt"] is None]
    empty = [i for i in p.images if i["alt"] is not None and not i["alt"].strip()]
    imgs_empty_alt = len(empty)
    # Components often default alt to "", so empty alt on a content image usually means "never written".
    suspect_empty = [i["src"] for i in empty if not i["decorative"] and (i["in_content"] or not p.landmarks & {"main", "article"})]
    host = urlparse(res["final_url"]).netloc.replace("www.", "")
    internal = set()
    for h in p.links:
        h = h.strip()
        if not h or h.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        u = urlparse(urljoin(res["final_url"], h))
        if u.netloc.replace("www.", "") == host:
            internal.add(u.path.rstrip("/") or "/")
    fake_links = sorted({h for h in p.links if FAKE_LINK_RE.search(h.strip())})

    page.update({
        "html_bytes": len(res["body"]),
        "text_chars": len(text),
        "text_ratio_pct": round(100 * len(text) / max(len(html), 1), 2),
        "words": len(text.split()),
        "lang": p.lang,
        "title": (p.title or "").strip() or None,
        "meta_description": p.meta.get("description"),
        "canonical": p.canonical,
        "meta_robots": p.meta.get("robots"),
        "x_robots_tag": res["headers"].get("x-robots-tag"),
        "og_title": p.meta.get("og:title"),
        "og_description": p.meta.get("og:description"),
        "og_image": bool(p.meta.get("og:image")),
        "twitter_card": p.meta.get("twitter:card"),
        "jsonld_types": types,
        "jsonld_parse_errors": ld_errors,
        "h1": [t for lvl, t in p.headings if lvl == 1],
        "headings": [f"h{lvl}: {t[:80]}" for lvl, t in p.headings[:40]],
        "heading_level_skipped": skipped,
        "landmarks": sorted(p.landmarks),
        "images": len(p.images),
        "images_missing_alt": len(imgs_no_alt),
        "images_missing_alt_samples": imgs_no_alt[:5],
        "images_empty_alt": imgs_empty_alt,
        "images_empty_alt_suspect": len(suspect_empty),
        "images_empty_alt_suspect_samples": suspect_empty[:5],
        "videos": p.videos,
        "videos_unlabelled": p.videos - p.videos_labelled,
        "links": len(p.links),
        "internal_link_paths": sorted(internal),
        "fake_links": fake_links[:10],
        "placeholder_text_hits": sorted({m.group(0).lower() for m in PLACEHOLDER_TEXT_RE.finditer(text)})[:10],
        "inline_base64_count": len(base64),
        "inline_base64_bytes": sum(len(b) for b in base64),
        "script_tags": p.scripts,
        # An empty JS shell has no h1. A page with an h1 but little text is usually
        # a photo grid or short list rendered on the server: flag it for review only.
        "likely_client_rendered": len(text) < 250 and p.scripts > 3 and not any(lvl == 1 for lvl, _ in p.headings),
        "low_text": len(text) < 250,
        "text_preview": text[:400],
    })
    return page


def robots_report(text):
    """Very small robots.txt reader: which AI bots are fully or partly blocked."""
    groups, agents, rules = [], [], []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, val = [s.strip() for s in line.split(":", 1)]
        key = key.lower()
        if key == "user-agent":
            if rules:
                groups.append((agents, rules))
                agents, rules = [], []
            agents.append(val.lower())
        elif key in ("allow", "disallow"):
            rules.append((key, val))
        elif key == "sitemap":
            pass
    if agents or rules:
        groups.append((agents, rules))

    def rules_for(bot):
        b = bot.lower()
        specific = [r for a, r in groups if any(x != "*" and x in b for x in a)]
        if specific:
            return [x for r in specific for x in r]
        return [x for a, r in groups if "*" in a for x in r]

    out = {}
    for bot in AI_BOTS:
        r = rules_for(bot)
        if any(k == "disallow" and v == "/" for k, v in r) and not any(k == "allow" and v == "/" for k, v in r):
            out[bot] = "blocked"
        elif any(k == "disallow" and v for k, v in r):
            out[bot] = "partially blocked: " + ", ".join(v for k, v in r if k == "disallow" and v)[:200]
        else:
            out[bot] = "allowed"
    sitemaps = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", text)
    return out, sitemaps


def site_files(base, ua):
    out = {}
    for path in ("/robots.txt", "/sitemap.xml", "/llms.txt", "/llms-full.txt"):
        res = fetch(urljoin(base, path), ua)
        body = decode(res["body"], res["headers"]) if res["body"] else ""
        ctype = res["headers"].get("content-type", "")
        looks_html = "<html" in body[:500].lower()
        entry = {"status": res["status"], "bytes": len(res["body"]), "content_type": ctype}
        if res.get("error"):
            entry["error"] = res["error"]
        if res["status"] == 200 and looks_html and path != "/sitemap.xml":
            entry["warning"] = "served HTML, probably a catch-all page rather than the real file"
        if path == "/robots.txt" and res["status"] == 200 and not looks_html:
            entry["ai_bots"], entry["sitemaps"] = robots_report(body)
        if path == "/sitemap.xml" and res["status"] == 200:
            entry["urls"] = len(re.findall(r"<loc>", body))
        if path in ("/llms.txt", "/llms-full.txt") and res["status"] == 200 and not looks_html:
            entry["starts_with_h1"] = body.lstrip().startswith("# ")
            entry["preview"] = body[:300]
        out[path] = entry
    return out


def sitemap_urls(base, ua, cap):
    res = fetch(urljoin(base, "/sitemap.xml"), ua)
    if res["status"] != 200:
        return []
    body = decode(res["body"], res["headers"])
    locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body)
    # sitemap index: follow child sitemaps one level deep
    if "<sitemapindex" in body:
        children = locs
        locs = []
        for child in children[:5]:
            r = fetch(child, ua)
            locs += re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", decode(r["body"], r["headers"]))
    host = urlparse(base).netloc.replace("www.", "")
    same = [u for u in locs if urlparse(u).netloc.replace("www.", "") == host]
    return same[:cap]


def score_hints(s, indexable):
    """Pre-fill the bot-detectable checks. 'review' means the agent must confirm in the source."""
    files = s["site_files"]
    ok200 = lambda path: files[path].get("status") == 200 and "warning" not in files[path]
    bots = files["/robots.txt"].get("ai_bots", {})
    blocked = [b for b, v in bots.items() if v == "blocked"]

    def verdict(fail, partial=False):
        return "fail" if fail else ("partial" if partial else "pass")

    hints = {
        "A1": "fail" if s["pages_likely_client_rendered"] else ("review" if s["pages_low_text"] else "pass"),
        "A3": "fail" if not ok200("/robots.txt") else ("review" if blocked else "pass"),
        "A4": verdict(not ok200("/sitemap.xml")),
        "A5": "review" if s["errors"] else "pass",
        "A6": verdict(bool(s["non_permanent_redirects"])),
        "A8": "review" if s["pages_not_linked_from_home"] else "pass",
        "B1": verdict(not ok200("/llms.txt")),
        "B2": verdict(not ok200("/llms-full.txt")),
        "C1": verdict(bool(s["pages_without_jsonld"])),
        "C4": verdict(any(p.get("jsonld_parse_errors") for p in indexable)),
        "D1": verdict(bool(s["duplicate_titles"])),
        "D2": verdict(bool(s["pages_missing_description"])),
        "D3": verdict(bool(s["pages_missing_canonical"])),
        "D5": verdict(any(not p.get("lang") for p in indexable)),
        "E1": verdict(bool(s["pages_without_single_h1"])),
        "E2": verdict(False, partial=bool(s["pages_with_heading_skips"])),
        "G1": verdict(s["total_images_missing_alt"] > 0, partial=s["total_images_empty_alt_suspect"] > 0),
        "G3": verdict(s["total_videos_unlabelled"] > 0),
        "H1": verdict(False, partial=bool(s["pages_low_text_ratio"])),
        "I1": verdict(bool(s["fake_links"])),
    }
    if blocked:
        hints["_note_A3"] = "blocked: " + ", ".join(blocked) + " (ask the author whether that's deliberate)"
    if s["errors"]:
        hints["_note_A5"] = "errors may be local-only (missing env vars, unseeded DB); check server logs and the live site"
    if s["total_images_empty_alt_suspect"]:
        hints["_note_G1"] = "empty alt on content images usually means a component defaults alt to \"\"; confirm in source"
    return hints


def print_hints(h):
    marks = {"pass": "ok", "fail": "FAIL", "partial": "part", "review": "check"}
    line = "  ".join(f"{k}:{marks.get(v, v)}" for k, v in h.items() if not k.startswith("_"))
    sys.stderr.write("bot_view score hints  " + line + "\n")
    for k, v in h.items():
        if k.startswith("_"):
            sys.stderr.write(f"  {k[1:]}: {v}\n")


def main():
    ap = argparse.ArgumentParser(description="See a site the way an AI crawler does (no JavaScript).")
    ap.add_argument("base", help="Base URL, e.g. https://example.com or http://localhost:3000")
    ap.add_argument("paths", nargs="*", help="Extra paths or full URLs to analyse")
    ap.add_argument("--sitemap", type=int, default=0, metavar="N", help="Also analyse up to N URLs from sitemap.xml")
    ap.add_argument("--ua", default="gptbot", choices=sorted(USER_AGENTS), help="User-Agent to send (default gptbot)")
    ap.add_argument("--pretty", action="store_true", help="Indent JSON output")
    # intermixed: paths may come before or after the options
    args = ap.parse_intermixed_args()

    base = args.base if "://" in args.base else "https://" + args.base
    ua = USER_AGENTS[args.ua]

    home = analyse_page(base, ua)
    origin = home.get("final_url") or base
    parsed = urlparse(origin)
    origin = f"{parsed.scheme}://{parsed.netloc}/"

    targets = []
    for p in args.paths:
        targets.append(p if "://" in p else urljoin(origin, p))
    sitemap_list = sitemap_urls(origin, ua, max(args.sitemap, 200)) if args.sitemap else []
    targets += sitemap_list[: args.sitemap]
    seen, pages = {base.rstrip("/"), origin.rstrip("/")}, [home]
    for t in targets:
        if t.rstrip("/") in seen:
            continue
        seen.add(t.rstrip("/"))
        pages.append(analyse_page(t, ua))

    ok = [p for p in pages if p.get("status") == 200 and "html_bytes" in p]
    is_noindex = lambda p: "noindex" in ((p.get("meta_robots") or "") + (p.get("x_robots_tag") or "")).lower()
    # Checks about how a page should present itself only apply to pages meant to be indexed.
    indexable = [p for p in ok if not is_noindex(p)]
    titles = [p.get("title") for p in indexable]
    home_links = set(home.get("internal_link_paths", []))
    known = {urlparse(p.get("final_url") or p["url"]).path.rstrip("/") or "/" for p in indexable}
    known |= {urlparse(u).path.rstrip("/") or "/" for u in sitemap_list}
    # Pages a crawler can only reach through the sitemap (or not at all). Often a client-only navbar.
    unlinked = sorted(k for k in known if k != "/" and k not in home_links)

    summary = {
        "base": base,
        "resolved_origin": origin,
        "user_agent": args.ua,
        "home_redirects": home.get("redirects", []),
        "non_permanent_redirects": [h for p in pages for h in p.get("redirects", []) if h.get("status") in (302, 303, 307)],
        "site_files": site_files(origin, ua),
        "pages_checked": len(pages),
        "pages_ok": len(ok),
        "pages_indexable": len(indexable),
        "pages_missing_description": [p["url"] for p in indexable if not p.get("meta_description")],
        "pages_missing_canonical": [p["url"] for p in indexable if not p.get("canonical")],
        "pages_without_jsonld": [p["url"] for p in indexable if not p.get("jsonld_types")],
        "pages_without_single_h1": [p["url"] for p in indexable if len(p.get("h1", [])) != 1],
        "duplicate_titles": sorted({t for t in titles if t and titles.count(t) > 1}),
        "pages_likely_client_rendered": [p["url"] for p in indexable if p.get("likely_client_rendered")],
        "pages_low_text": [p["url"] for p in indexable if p.get("low_text") and not p.get("likely_client_rendered")],
        # small pages with a low ratio are harmless; only flag ones big enough to risk truncation
        "pages_low_text_ratio": [f'{p["url"]} ({p["text_ratio_pct"]}%, {p["html_bytes"]} bytes)' for p in indexable if p.get("text_ratio_pct", 100) < 2 and p.get("html_bytes", 0) > LOW_RATIO_MIN_BYTES],
        "pages_with_heading_skips": [p["url"] for p in indexable if p.get("heading_level_skipped")],
        "total_images_missing_alt": sum(p.get("images_missing_alt", 0) for p in indexable),
        "total_images_empty_alt": sum(p.get("images_empty_alt", 0) for p in indexable),
        "total_images_empty_alt_suspect": sum(p.get("images_empty_alt_suspect", 0) for p in indexable),
        "pages_with_suspect_empty_alt": [f'{p["url"]} ({p["images_empty_alt_suspect"]})' for p in indexable if p.get("images_empty_alt_suspect")],
        "home_internal_links": home.get("internal_link_paths", []),
        "pages_not_linked_from_home": unlinked,
        "total_videos_unlabelled": sum(p.get("videos_unlabelled", 0) for p in indexable),
        "fake_links": sorted({l for p in indexable for l in p.get("fake_links", [])}),
        "noindexed_pages": [p["url"] for p in ok if is_noindex(p)],
        "errors": [{"url": p["url"], "status": p.get("status"), "error": p.get("error")} for p in pages if p not in ok],
    }
    summary["score_hints"] = score_hints(summary, indexable)
    print_hints(summary["score_hints"])
    json.dump({"summary": summary, "pages": pages}, sys.stdout, indent=2 if args.pretty else None, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
