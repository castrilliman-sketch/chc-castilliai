#!/usr/bin/env python3
"""Validate the built CHC site: titles, descriptions, H1s, schema, no ai.studio links, no LegalService, no personal email in JSON-LD."""
import sys, re, json, html, os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from seo_width import title_px, desc_px, TITLE_MAX_PX, TITLE_MAX_CHARS, TITLE_MIN_CHARS, DESC_MAX_PX, DESC_MAX_CHARS, repeated_words

src = sys.argv[1] if len(sys.argv) > 1 else ROOT
CONTACT = "danwyatt398@gmail.com"

def walk_pages(root):
    paths = []
    for d, dirs, fs in os.walk(root):
        dirs[:] = [x for x in dirs if x not in {".git", "scripts", "__pycache__", "assets"}]
        for f in fs:
            if f == "index.html":
                rel = os.path.relpath(d, root)
                paths.append("/" if rel == "." else "/" + rel.replace("\\", "/") + "/")
    return sorted(set(paths))

def get(p):
    fp = os.path.join(src, p.lstrip("/"))
    if p.endswith("/"):
        fp = os.path.join(fp, "index.html")
    elif not fp.endswith(".html"):
        fp = os.path.join(src, p.lstrip("/"), "index.html") if p != "/" else os.path.join(src, "index.html")
    return open(fp, encoding="utf-8").read()

def norm(t):
    return re.sub(r"\s+", " ", html.unescape(t)).strip()

def visible(h):
    h = re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S)
    return norm(re.sub(r"<[^>]+>", " ", h))

def attr(h, pattern):
    m = re.search(pattern, h, re.I | re.S)
    return html.unescape(m.group(1)) if m else ""

bad = 0
title_map = {}
paths = walk_pages(src)
print(f"Checking {len(paths)} pages in {src}")

# required files
for f in ["favicon.svg", "apple-touch-icon.png", "og.png", "robots.txt", "sitemap.xml", "CNAME", "assets/eligibility.js", "styles.css"]:
    if not os.path.isfile(os.path.join(src, f)):
        print("MISSING FILE", f); bad += 1

robots = open(os.path.join(src, "robots.txt"), encoding="utf-8").read()
if "Sitemap: https://chc.castilliai.com/sitemap.xml" not in robots:
    print("ROBOTS MISSING SITEMAP LINE"); bad += 1
if "NexusAI" in robots:
    print("NEXUSAI IN ROBOTS"); bad += 1

sitemap = open(os.path.join(src, "sitemap.xml"), encoding="utf-8").read()
for p in paths:
    loc = f"https://chc.castilliai.com{p}"
    if loc not in sitemap:
        print("SITEMAP MISSING", loc); bad += 1

for p in paths:
    h = get(p)
    vis = visible(h)

    if 'lang="en-GB"' not in h and "lang='en-GB'" not in h:
        print("LANG NOT en-GB", p); bad += 1
    if "ai.studio" in h.lower() or "ais-pre-" in h.lower() or "run.app" in h.lower():
        print("AISTUDIO LINK", p); bad += 1
    if "NexusAI" in h:
        print("NEXUSAI", p); bad += 1
    if "LegalService" in h:
        print("LEGALSERVICE SCHEMA", p); bad += 1
    if "cheaper than Beacon" in h and "not a general claim that we are cheaper than Beacon" not in h:
        print("UNSUPPORTED BEACON CLAIM", p); bad += 1
    if "clinical sign-off" in h.lower() or "clinical lead" in h.lower():
        print("CLINICAL SIGNOFF CLAIM", p); bad += 1
    for name in ("Margaret Hughes", "Sarah Jenkins", "David Croft", "Helen Miller", "Eleanor Vance", "Dorothy Vance"):
        if name in h:
            print("STAFF/DEMO NAME", p, name); bad += 1

    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try:
            j = json.loads(raw)
        except Exception as e:
            print("JSON-LD PARSE FAIL", p, e); bad += 1
            continue
        blob = json.dumps(j)
        if CONTACT in blob or "@gmail.com" in blob:
            print("EMAIL IN JSON-LD", p); bad += 1
        if "LegalService" in blob:
            print("LEGALSERVICE SCHEMA", p); bad += 1
        nodes = j if isinstance(j, list) else j.get("@graph", [j])
        if isinstance(j, dict) and j.get("@type") == "FAQPage":
            nodes = [j]
        for node in nodes if isinstance(nodes, list) else [nodes]:
            if isinstance(node, dict) and node.get("@type") == "FAQPage":
                for q in node.get("mainEntity") or []:
                    for t in (q.get("name"), (q.get("acceptedAnswer") or {}).get("text")):
                        if t and norm(t) not in vis:
                            print("FAQ TEXT NOT VISIBLE", p, norm(t)[:90]); bad += 1

    title = attr(h, r"<title>(.*?)</title>")
    desc = attr(h, r'<meta\s+name="description"\s+content="(.*?)"')
    if not desc:
        desc = attr(h, r'<meta\s+content="(.*?)"\s+name="description"')
    canon = attr(h, r'<link\s+rel="canonical"\s+href="(.*?)"')
    expected = "https://chc.castilliai.com" + p
    if canon != expected:
        print("CANONICAL", p, canon, "expected", expected); bad += 1
    if f'property="og:url" content="{expected}"' not in h and f"property='og:url' content='{expected}'" not in h:
        # allow either quote order
        if 'property="og:url"' not in h or expected not in attr(h, r'<meta\s+property="og:url"\s+content="(.*?)"'):
            print("OG URL", p); bad += 1
    if "og:image" not in h:
        print("NO OG IMAGE", p); bad += 1
    if not re.search(r'<link[^>]+rel=["\'][^"\']*icon', h, re.I):
        print("NO FAVICON MARKUP", p); bad += 1

    tw, dw = title_px(title), desc_px(desc)
    if tw > TITLE_MAX_PX:
        print(f"TITLE TOO WIDE {tw:.0f}px>{TITLE_MAX_PX} {p} {title}"); bad += 1
    if len(title) > TITLE_MAX_CHARS:
        print(f"TITLE TOO LONG {len(title)}>{TITLE_MAX_CHARS} {p} {title}"); bad += 1
    if title and len(title) < TITLE_MIN_CHARS:
        print(f"TITLE SHORT {len(title)}<{TITLE_MIN_CHARS} {p} {title}"); bad += 1
    reps = repeated_words(title)
    if reps:
        print(f"TITLE REPEATED WORDS {reps} {p} {title}"); bad += 1
    if dw > DESC_MAX_PX:
        print(f"DESC TOO WIDE {dw:.0f}px>{DESC_MAX_PX} {p} {desc[:140]}"); bad += 1
    if len(desc) > DESC_MAX_CHARS:
        print(f"DESC TOO LONG {len(desc)}>{DESC_MAX_CHARS} {p} {desc[:140]}"); bad += 1
    title_map.setdefault(title.lower(), []).append((p, title))

    heads = re.findall(r"<h([1-6])\b[^>]*>(.*?)</h\1>", h, re.S | re.I)
    texts = [norm(re.sub(r"<[^>]+>", "", body)) for _, body in heads]
    h1s = [norm(re.sub(r"<[^>]+>", "", body)) for level, body in heads if level == "1"]
    if len(h1s) != 1:
        print("H1 COUNT", p, len(h1s), h1s); bad += 1
    for text, c in Counter(t for t in texts if t).items():
        if c > 1:
            print("DUP HEADING", p, c, text); bad += 1

    if p == "/":
        main = re.search(r"<main\b[^>]*>(.*?)</main>", h, re.S | re.I)
        main_html = main.group(1) if main else h
        main_wo_h1 = re.sub(r"<h1\b[^>]*>.*?</h1>", " ", main_html, flags=re.S | re.I)
        body_words = set(re.findall(r"[a-z0-9']+", visible(main_wo_h1).lower()))
        for h1 in h1s:
            missing = []
            for w in re.findall(r"[A-Za-z0-9']+", h1):
                lw = w.lower()
                if len(lw) <= 1 or lw in {
                    "a","an","and","as","at","be","by","for","from","if","in","into","is","it",
                    "of","on","or","the","to","vs","we","you","your","when","what","who","how",
                    "why","with","our","this","that","are","was","were","not","its",
                }:
                    continue
                if lw not in body_words:
                    missing.append(w)
            if missing:
                print("H1 WORDS NOT IN TEXT", p, missing, "from", h1); bad += 1

home = get("/")
if "we cannot help with litigation" not in visible(home).lower():
    print("FOOTER DISCLAIMER MISSING"); bad += 1
if "not VAT registered" not in visible(get("/pricing/")):
    print("VAT STATUS MISSING ON PRICING"); bad += 1
if "not a law firm or solicitors" not in visible(home).lower():
    print("FOOTER DISCLAIMER INCOMPLETE"); bad += 1

for title_key, items in sorted(title_map.items()):
    if len(items) > 1:
        pages = ", ".join(p for p, _ in items)
        print(f"DUPLICATE TITLE {pages} {items[0][1]}"); bad += 1

print(f"Checked {len(paths)} pages, problems: {bad}")
sys.exit(1 if bad else 0)
