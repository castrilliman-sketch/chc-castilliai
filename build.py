#!/usr/bin/env python3
"""Build the CHC Appeals Navigator static site into this repository (GitHub Pages root)."""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
from seo_width import (  # noqa: E402
    TITLE_MAX_CHARS,
    TITLE_MAX_PX,
    TITLE_MIN_CHARS,
    DESC_MAX_CHARS,
    DESC_MAX_PX,
    desc_px,
    repeated_words,
    title_px,
)

BASE = "https://chc.castilliai.com"
NAME = "CHC Appeals Navigator"
LEGAL_NAME = "Daniel Wyatt t/a CastilliAI"
AUTHOR = "Daniel Wyatt"
CONTACT_EMAIL = "danwyatt398@gmail.com"
REVIEW_DATE = "24 November 2026"
TODAY = date(2026, 11, 24).isoformat()
STRIPE_STAGE1 = "https://buy.stripe.com/6oUeVe2Nia6Y5pDbPFa3u0b"
STRIPE_STAGE2 = "https://buy.stripe.com/4gM9ATgBCeMZ2H64ti0ZW02"
GOVUK_FRAMEWORK = "https://www.gov.uk/government/publications/national-framework-for-nhs-continuing-healthcare-and-nhs-funded-nursing-care"
GOVUK_DST = "https://www.gov.uk/government/publications/nhs-continuing-healthcare-decision-support-tool/nhs-continuing-healthcare-decision-support-tool-guidance"
GOVUK_LEAFLET = "https://www.gov.uk/government/publications/nhs-continuing-healthcare-and-nhs-funded-nursing-care-public-information-leaflet/public-information-leaflet-nhs-continuing-healthcare-and-nhs-funded-nursing-care--2"
NHS_FNC = "https://www.nhs.uk/social-care-and-support/money-work-and-benefits/nhs-funded-nursing-care/"
NHS_CHC = "https://www.nhs.uk/social-care-and-support/money-work-and-benefits/nhs-continuing-healthcare/"
NHSE_IR = "https://www.england.nhs.uk/wp-content/uploads/2020/03/nhs-continuing-healthcare-independent-review-process.pdf"

DISCLAIMER = (
    "CHC Appeals Navigator is an independent advocacy service provided by Daniel Wyatt, trading as CastilliAI. "
    "We are not a law firm or solicitors, we do not give legal advice, and we cannot help with litigation. "
    "Daniel has 20 years’ experience in UK finance, including complaints handling, debt purchasing, credit control and leading teams."
)

NAV = [
    ("/how-it-works/", "How it works"),
    ("/pricing/", "Prices"),
    ("/guides/", "Guides"),
    ("/faq/", "FAQ"),
    ("/eligibility/", "Free check"),
]

FOOTER_LINKS = [
    ("/about/", "About"),
    ("/pricing/", "Prices"),
    ("/eligibility/", "Free check"),
    ("/guides/", "Guides"),
    ("/faq/", "FAQ"),
    ("/privacy/", "Privacy notice"),
    ("/terms/", "Terms"),
    ("/complaints/", "Complaints"),
]

STAGES = [
    {
        "n": 0,
        "name": "Stage 0 — Eligibility check",
        "price": "Free",
        "period": "No charge",
        "blurb": "Ten questions to help you see whether a closer look is worthwhile, before you spend anything. This is not an official NHS assessment.",
        "cta": "Take the free check",
        "href": "/eligibility/",
        "primary": False,
    },
    {
        "n": 1,
        "name": "Stage 1 — Evidence review and verdict",
        "price": "£349",
        "period": "Fixed one-off fee",
        "blurb": "We review the records you upload, map them to the 12 Decision Support Tool domains, and send a written Yes, No or Maybe verdict. If the answer is No, you stop there.",
        "cta": "Start Stage 1 — £349",
        "href": STRIPE_STAGE1,
        "primary": True,
        "features": [
            "Document review and a 12-domain evidence map with page citations where the records allow",
            "A written strength-and-weakness report and a Yes, No or Maybe verdict",
            "Human review by Daniel Wyatt before the report is sent",
        ],
    },
    {
        "n": 2,
        "name": "Stage 2 — Local resolution appeal pack",
        "price": "£799",
        "period": "Or 3 × £266.33 a month via GoCardless, subject to status",
        "blurb": "The first formal appeal after a refusal: a Local Resolution pack for the ICB, including a formal letter, commentary on the DST, and preparation for a local resolution meeting.",
        "cta": "Instruct Stage 2 — £799",
        "href": STRIPE_STAGE2,
        "primary": False,
        "note": "If your Stage 1 verdict was Maybe, you instruct Stage 2, and the ICB upholds the refusal at local resolution, we refund 25% of the Stage 2 fee when we have the final written decision.",
    },
    {
        "n": 3,
        "name": "Stage 3 — Independent review panel",
        "price": "£1,499",
        "period": "Or 3 × £499.66 a month via GoCardless, subject to status",
        "blurb": "A submission to NHS England for an independent review, hearing preparation, and representation at the panel where that is part of the service you have asked for.",
        "cta": "Email to instruct Stage 3",
        "href": f"mailto:{CONTACT_EMAIL}?subject=Stage%203%20Independent%20review",
        "primary": False,
    },
    {
        "n": 4,
        "name": "Stage 4 — Ombudsman complaint",
        "price": "£399",
        "period": "Optional add-on",
        "blurb": "Help drafting a complaint to the Parliamentary and Health Service Ombudsman where you remain dissatisfied after an independent review.",
        "cta": "Email to instruct Stage 4",
        "href": f"mailto:{CONTACT_EMAIL}?subject=Stage%204%20Ombudsman%20complaint",
        "primary": False,
    },
    {
        "n": 5,
        "name": "Stage 5 — Retrospective review of past care fees",
        "price": "£1,499 + 8% of recovery",
        "period": "Fixed fee plus 8% of funds recovered",
        "blurb": "A review of a past period of care that was not assessed, or that you believe was wrongly assessed, including after a relative has died.",
        "cta": "Email to instruct Stage 5",
        "href": f"mailto:{CONTACT_EMAIL}?subject=Stage%205%20Retrospective%20review",
        "primary": False,
    },
]


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def validate_meta(path: str, title: str, desc: str) -> None:
    errors = []
    if not (TITLE_MIN_CHARS <= len(title) <= TITLE_MAX_CHARS):
        errors.append(f"title length {len(title)} (need {TITLE_MIN_CHARS}-{TITLE_MAX_CHARS})")
    px = title_px(title)
    if px > TITLE_MAX_PX:
        errors.append(f"title {px:.1f}px > {TITLE_MAX_PX}")
    reps = repeated_words(title)
    if reps:
        errors.append(f"repeated words {reps}")
    if len(desc) > DESC_MAX_CHARS:
        errors.append(f"desc length {len(desc)} > {DESC_MAX_CHARS}")
    if desc_px(desc) > DESC_MAX_PX:
        errors.append(f"desc {desc_px(desc):.1f}px > {DESC_MAX_PX}")
    if errors:
        raise SystemExit(f"META FAIL {path}: {title!r} / {desc!r} -> {errors}")


def nav_html(current: str) -> str:
    links = []
    for href, label in NAV:
        cur = ' aria-current="page"' if current == href or (href != "/" and current.startswith(href)) else ""
        links.append(f'<a href="{href}"{cur}>{esc(label)}</a>')
    desktop = "\n   ".join(links)
    mobile = "\n    ".join(links + [f'<a href="/about/">About</a>', f'<a href="{STRIPE_STAGE1}">Start — £349</a>'])
    return f"""<nav class="main" aria-label="Main">{desktop}
   <a class="btn btn-primary btn-sm" href="{STRIPE_STAGE1}">Start — £349</a>
  </nav>
  <details class="menu">
   <summary><span class="sr">Open</span></summary>
   <nav aria-label="Mobile">{mobile}</nav>
  </details>"""


def footer_html() -> str:
    items = "\n    ".join(f'<li><a href="{h}">{esc(l)}</a></li>' for h, l in FOOTER_LINKS)
    return f"""<footer>
 <div class="wrap cols">
  <div>
   <p>{esc(DISCLAIMER)}</p>
   <p>Guidance: <a href="{GOVUK_FRAMEWORK}">National Framework for NHS Continuing Healthcare (GOV.UK)</a>. This site covers England.</p>
   <p>Prices are fixed and no VAT is charged; we are not VAT registered.</p>
  </div>
  <div>
   <p><strong style="color:#fff">Pages</strong></p>
   <ul>
    {items}
   </ul>
  </div>
  <div>
   <p>Contact: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
   <p><a href="https://www.castilliai.com/">CastilliAI</a></p>
   <p>© 2026 {esc(LEGAL_NAME)}</p>
  </div>
 </div>
</footer>
<div class="sticky" role="region" aria-label="Quick actions">
 <a class="btn btn-primary" href="{STRIPE_STAGE1}">Start — £349</a>
 <a class="btn btn-secondary" href="/eligibility/">Free check</a>
</div>"""


def offer_schema() -> list[dict]:
    return [
        {"@type": "Offer", "name": "Stage 0 — Free eligibility check", "price": "0", "priceCurrency": "GBP"},
        {"@type": "Offer", "name": "Stage 1 — Evidence review, report and Yes/No/Maybe verdict", "price": "349", "priceCurrency": "GBP", "url": STRIPE_STAGE1},
        {"@type": "Offer", "name": "Stage 2 — Local resolution appeal pack", "price": "799", "priceCurrency": "GBP", "url": STRIPE_STAGE2},
        {"@type": "Offer", "name": "Stage 3 — Independent review panel submission and hearing preparation", "price": "1499", "priceCurrency": "GBP"},
        {"@type": "Offer", "name": "Stage 4 — Ombudsman complaint (optional add-on)", "price": "399", "priceCurrency": "GBP"},
        {"@type": "Offer", "name": "Stage 5 — Retrospective review of past care fees (plus 8% of recovery)", "price": "1499", "priceCurrency": "GBP"},
    ]


def base_schema(extra: list | None = None) -> str:
    graph = [
        {
            "@type": "Organization",
            "@id": BASE + "/#organization",
            "name": NAME,
            "legalName": LEGAL_NAME,
            "url": BASE + "/",
            "founder": {"@type": "Person", "name": AUTHOR, "jobTitle": "Founder"},
            "parentOrganization": {"@type": "Organization", "name": "CastilliAI", "url": "https://www.castilliai.com/"},
            "areaServed": {"@type": "Country", "name": "United Kingdom"},
        },
        {
            "@type": "ProfessionalService",
            "@id": BASE + "/#service",
            "name": NAME,
            "url": BASE + "/",
            "image": BASE + "/og.png",
            "serviceType": "NHS Continuing Healthcare appeal preparation and advocacy",
            "provider": {"@id": BASE + "/#organization"},
            "areaServed": {"@type": "Country", "name": "United Kingdom"},
            "description": "Independent advocacy (not a law firm) helping families prepare NHS Continuing Healthcare funding appeals. Pay per stage.",
            "offers": offer_schema(),
        },
        {
            "@type": "WebSite",
            "@id": BASE + "/#website",
            "url": BASE + "/",
            "name": NAME,
            "publisher": {"@id": BASE + "/#organization"},
            "inLanguage": "en-GB",
        },
    ]
    if extra:
        graph.extend(extra)
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=None)


def faq_schema(pairs: list[tuple[str, str]]) -> dict:
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in pairs
        ],
    }


def article_schema(url: str, title: str, desc: str) -> dict:
    return {
        "@type": "Article",
        "headline": title,
        "description": desc,
        "dateModified": TODAY,
        "author": {"@type": "Person", "name": AUTHOR},
        "publisher": {"@id": BASE + "/#organization"},
        "mainEntityOfPage": url,
        "inLanguage": "en-GB",
    }


def render_faq(pairs: list[tuple[str, str]]) -> str:
    blocks = []
    for q, a in pairs:
        blocks.append(
            f"<details><summary>{esc(q)}</summary><div class=\"ans\"><p>{a}</p></div></details>"
        )
    # answers may contain links — pass already-escaped or raw HTML in a
    return "\n  ".join(blocks)


def page(path: str, title: str, desc: str, h1: str, body: str, extra_schema=None, extra_head: str = "", article: bool = False) -> str:
    validate_meta(path, title, desc)
    url = BASE + path
    schema_extra = list(extra_schema or [])
    if article:
        schema_extra.append(article_schema(url, title, desc))
    schema = base_schema(schema_extra or None)
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#16324f">
<meta name="author" content="{esc(AUTHOR)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(NAME)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="en_GB">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{BASE}/og.png">
<link rel="stylesheet" href="/styles.css">
<script type="application/ld+json">{schema}</script>
{extra_head}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap"><a class="brand" href="/"><img src="/favicon.svg" alt="" width="32" height="32">{esc(NAME)}</a>
  {nav_html(path)}
</div></header>
<main id="main">
{body}
</main>
{footer_html()}
</body>
</html>
"""


def byline(kind: str = "guide") -> str:
    if kind == "guide":
        return (
            f'<p class="byline">By {esc(AUTHOR)}, {esc(LEGAL_NAME)}. Written in plain English and checked by him. '
            f"Last reviewed {REVIEW_DATE}. This is general information for England, not legal or medical advice, "
            f"and not an official NHS assessment.</p>"
        )
    return f'<p class="byline">Last updated {REVIEW_DATE}.</p>'


def sources(items: list[tuple[str, str]]) -> str:
    lis = "\n  ".join(f'<li><a href="{url}">{esc(label)}</a></li>' for label, url in items)
    return f'<div class="sources"><h2>Sources</h2><ul>\n  {lis}\n </ul></div>'


def crumb(*parts: tuple[str, str]) -> str:
    bits = ['<a href="/">Home</a>']
    for href, label in parts:
        bits.append(f'<a href="{href}">{esc(label)}</a>' if href else esc(label))
    return '<p class="crumb">' + " · ".join(bits) + "</p>"



HOME_FAQS = [
    (
        "What is NHS Continuing Healthcare?",
        "NHS Continuing Healthcare (CHC) is a package of ongoing care arranged and funded solely by the NHS for adults who have been assessed as having a primary health need. It can be provided in a care home, a hospice or in the person's own home. It is not means-tested. The process is set out in the National Framework, which applies in England.",
    ),
    (
        "What happens after I pay £349?",
        "You set up your case and upload the records you have: care notes, GP records, hospital letters, the assessment and the decision letter. We map the evidence against the 12 Decision Support Tool domains and send you a written report with a Yes, No or Maybe verdict. You then decide whether to go further.",
    ),
    (
        "Are you solicitors?",
        "No. We are independent advocates, not a law firm and not a claims management company. We do not give legal or medical advice. Where you need a legal remedy, we will tell you and explain the options available to you.",
    ),
    (
        "What if Stage 1 says I don't have a case?",
        "You stop there with nothing more to pay. Because you pay per stage, you are never locked in. If the Stage 1 verdict is \"Maybe\" and you proceed to Stage 2 and lose, we offer a 25% refund of the Stage 2 fee.",
    ),
    (
        "Can you guarantee funding?",
        "No. Nobody can guarantee a CHC decision. The integrated care board decides eligibility. What we do is make sure the evidence is organised, mapped to the right domains and argued clearly, so the decision is made on the full picture.",
    ),
    (
        "What happens to my relative's records?",
        "Health records are special category data under UK GDPR. We use them only to prepare your case, we never sell them, and you can ask us to delete them. Read our privacy notice.",
    ),
]

FAQ_PAIRS = HOME_FAQS + [
    (
        "How long do I have to ask the ICB to look at the decision again?",
        "The ICB should tell you, in the decision letter, how and by when to ask for a review. In practice, integrated care boards commonly ask for a local resolution request within 6 months of the written decision. The older national timeframes, and many ICB policies, also allow a later request where there is a good reason and the records can still be obtained. Read the letter and the ICB's published process, and do not wait if you can help it.",
    ),
    (
        "What if I miss that 6-month point?",
        "You may still be able to ask. Late requests are sometimes accepted. If the period of care was never properly assessed, you may also be able to ask the ICB to look at that past period. Get advice promptly rather than assuming the file is closed for good.",
    ),
    (
        "What happens after local resolution?",
        "If you still disagree once the ICB has finished its local resolution process, you can apply to NHS England for an independent review of the eligibility decision or of the procedure the ICB followed. NHS England may first ask the ICB to try further local resolution. If you remain dissatisfied after an independent review, you can complain to the Parliamentary and Health Service Ombudsman.",
    ),
    (
        "Does a Priority or two Severe scores guarantee eligibility?",
        "No score combination guarantees a result. Official Decision Support Tool guidance says a clear recommendation of eligibility would be expected where there is a Priority level in one of the four domains that have that level (breathing, behaviour, drug therapies and medication, and altered states of consciousness), or two or more Severe levels across the domains. Other combinations may also indicate a primary health need. The ICB still has to decide, looking at the nature, intensity, complexity and unpredictability of the person's needs as a whole.",
    ),
    (
        "Can the NHS ignore a need because it is well managed?",
        "The National Framework is clear that the decision should not sideline a need just because it is successfully managed: well-managed needs are still needs. The only exception it describes is where management has permanently reduced or removed an ongoing need, so that active management is reduced or no longer required. The Decision Support Tool guidance also cautions that this principle should not be applied as if routine medication or care were simply not there.",
    ),
    (
        "Can an executor ask about a relative who has died?",
        "Yes. A family or executor can ask the ICB to consider a past period of care, including after a death, especially where there was no proper CHC assessment at the time. If a primary health need is later found for that period, the ICB may need to refund care fees that should have been NHS-funded. The exact process and any redress depend on the facts and current guidance.",
    ),
    (
        "Should I accept NHS-funded nursing care instead of a full CHC decision?",
        "FNC is a weekly NHS contribution towards registered nursing in a nursing home. It is not the same as full CHC, which funds the whole agreed care package. The standard FNC rate from 1 April 2026 is £267.68 a week. You should normally be assessed for CHC before an FNC decision is made. If you are only being offered FNC, it is worth checking that a proper CHC assessment was done and that you are content with the reasons.",
    ),
    (
        "Do you use my family's records to train public AI models?",
        "No. We never sell your information or use your family's records to train public AI models. See the privacy notice for how we use information.",
    ),
]


def home_page() -> str:
    faqs = render_faq([(q, esc(a)) for q, a in HOME_FAQS])
    body = f"""<section class="hero">
 <div class="wrap">
  <p class="eyebrow">NHS Continuing Healthcare appeals · England</p>
  <h1>Refused NHS Continuing Healthcare funding?</h1>
  <p class="lead">We help families appeal. If your parent or relative has been turned down for CHC, or given only nursing care contributions (FNC), we review the evidence, tell you honestly whether you have grounds, and prepare the appeal with you. Fixed prices. Pay one stage at a time.</p>
  <div class="cta-row">
   <a class="btn btn-primary" href="{STRIPE_STAGE1}">Start your appeal — £349</a>
   <a class="btn btn-secondary" href="/eligibility/">Free 10-question eligibility check</a>
  </div>
  <p class="small">£349 buys the Stage 1 evidence review and a clear Yes, No or Maybe verdict. If the answer is No, you stop there.</p>
  <ul class="trust">
   <li>Independent advocates, not a law firm</li>
   <li>Fixed fee per stage, no lock-in</li>
   <li>14-day cooling-off period</li>
   <li>Based on the NHS National Framework 2022</li>
  </ul>
 </div>
</section>

<section>
 <div class="wrap grid2">
  <div class="card yes">
   <h2>Is this right for your family?</h2>
   <h3>This is for you if</h3>
   <ul class="ticks">
    <li>A parent or relative is in a care home or receiving complex care at home</li>
    <li>They have been refused CHC funding, or awarded FNC only</li>
    <li>You are within 6 months of the decision letter, or you have a past period you want looked at</li>
    <li>You cannot justify several thousand pounds for a solicitor</li>
   </ul>
  </div>
  <div class="card no">
   <h3>This is not for you if</h3>
   <ul class="crosses">
    <li>You need legal advice (we are advocates, not solicitors)</li>
    <li>You want a guarantee of funding (nobody can guarantee that)</li>
   </ul>
  </div>
 </div>
</section>

<section class="alt" id="how">
 <div class="wrap">
  <h2>How it works</h2>
  <div class="grid4">
   <div class="card"><div class="step-n">1</div><h3>Upload your records</h3><p>Care notes, GP records, hospital letters, the assessment and the decision letter. Handwritten care logs and medication charts are fine.</p></div>
   <div class="card"><div class="step-n">2</div><h3>We map the evidence</h3><p>Each relevant fact is tagged to the 12 Decision Support Tool domains, with the document and page where we can show it.</p></div>
   <div class="card"><div class="step-n">3</div><h3>You get a verdict</h3><p>A written Yes, No or Maybe, with the strengths and weaknesses of the case, reviewed by {esc(AUTHOR)} before it goes out.</p></div>
   <div class="card"><div class="step-n">4</div><h3>We prepare the appeal</h3><p>If you want to go further, the next stage is a letter and pack for local resolution. You decide, stage by stage.</p></div>
  </div>
  <p class="small" style="margin-top:1.2em"><a href="/how-it-works/">Read the full process</a> · <a href="/guides/">Guides to the rules</a></p>
 </div>
</section>

<section id="pricing">
 <div class="wrap split">
  <div>
   <h2>What you get at Stage 1</h2>
   <p>Stage 1 is an evidence review and verdict for a fixed £349. It is designed so you can find out where you stand without signing up for a long case.</p>
   <ul class="ticks">
    <li>A domain-by-domain reading of the records you send</li>
    <li>A clear Yes, No or Maybe verdict</li>
    <li>The option to stop with nothing more to pay</li>
   </ul>
   <p><a href="/pricing/">See every stage and fee</a></p>
  </div>
  <div class="price-box">
   <h3>Stage 1: Evidence review and verdict</h3>
   <p class="amt">£349</p>
   <p>Fixed fee. 14-day cooling-off period. Pay per stage, stop any time.</p>
   <a class="btn btn-primary" href="{STRIPE_STAGE1}">Start your appeal — £349</a>
   <p class="small" style="margin:.8em 0 0"><a href="/eligibility/" style="color:#fff">Or start with the free check</a></p>
  </div>
 </div>
</section>

<section class="alt">
 <div class="wrap">
  <h2>Clear, fixed prices</h2>
  <table class="prices">
   <thead><tr><th>Stage</th><th>What you get</th><th>Fee</th></tr></thead>
   <tbody>
    <tr><td class="stage">Stage 0</td><td>Free eligibility check</td><td class="amt">£0</td></tr>
    <tr class="featured"><td class="stage">Stage 1</td><td>Evidence review, report and Yes / No / Maybe verdict</td><td class="amt">£349</td></tr>
    <tr><td class="stage">Stage 2</td><td>Local resolution appeal pack<span class="sub">Optional 25% refund if Stage 1 was Maybe and the ICB upholds the refusal</span></td><td class="amt">£799</td></tr>
    <tr><td class="stage">Stage 3</td><td>Independent review panel preparation</td><td class="amt">£1,499</td></tr>
    <tr><td class="stage">Stage 4</td><td>Ombudsman complaint (optional)</td><td class="amt">£399</td></tr>
    <tr><td class="stage">Stage 5</td><td>Retrospective review of past care fees<span class="sub">Plus 8% of any recovery</span></td><td class="amt">£1,499</td></tr>
   </tbody>
  </table>
  <p class="note">Payment plans via GoCardless are offered on some later stages, subject to status. <a href="/pricing/">Full pricing and how to pay</a>.</p>
 </div>
</section>

<section id="faq">
 <div class="wrap" style="max-width:800px">
  <h2>Common questions</h2>
  {faqs}
  <p><a href="/faq/">More questions and answers</a></p>
 </div>
</section>

<section class="final">
 <div class="wrap">
  <h2>Find out where you stand</h2>
  <p class="lead" style="margin:0 auto">Get an honest verdict on your relative's case for a fixed £349, or start with the free check.</p>
  <div class="cta-row">
   <a class="btn btn-primary" href="{STRIPE_STAGE1}">Start your appeal — £349</a>
   <a class="btn btn-secondary" href="/eligibility/">Free 10-question eligibility check</a>
  </div>
 </div>
</section>"""
    return page(
        "/",
        "CHC Appeals Navigator — help after an NHS funding refusal",
        "Refused NHS Continuing Healthcare funding? We review the evidence and give a Yes, No or Maybe verdict for £349. Pay per stage.",
        "Refused NHS Continuing Healthcare funding?",
        body,
        extra_schema=[faq_schema(HOME_FAQS)],
    )


def about_page() -> str:
    body = f"""<section class="legal">
 <div class="wrap prose">
  {crumb(("/about/", "About"))}
  <h1>About Daniel Wyatt and this service</h1>
  {byline("page")}
  <p>CHC Appeals Navigator is run by {esc(AUTHOR)}, trading as CastilliAI. I help families prepare and present NHS Continuing Healthcare funding appeals in England.</p>
  <h2>My background</h2>
  <p>I have spent 20 years in finance and complaints work. I have sat on both sides of that fence: dealing with formal complaints, and helping consumers understand their rights when a process feels stacked against them. I now write plain-English guidance and, with this service, help families organise the evidence that an ICB or an independent review will actually look at.</p>
  <h2>How I work, and how the guidance is checked</h2>
  <p>Every guide on this site is written in plain English and checked by me before it is published. I review it against the current National Framework and the official Decision Support Tool guidance. Each guide shows a last-reviewed date and links to the government sources it relies on.</p>
  <p>Stage 1 reports are also reviewed by me before they are sent to you. Where I use tools to help organise a large set of records, the judgement in the report is mine. I will tell you honestly if I do not think you have a case.</p>
  <h2>What I am not</h2>
  <p>I am not a solicitor, a barrister or a registered clinician. This service is independent advocacy and case preparation, not regulated legal advice and not medical advice. I will say so if a legal remedy looks necessary, and explain the options available to you.</p>
  <p>Eligibility is always decided by the integrated care board, not by me. Nobody can guarantee a CHC decision.</p>
  <h2>The trading name</h2>
  <p>I trade as CastilliAI. CHC Appeals Navigator is one of my services. You can also find me at <a href="https://www.castilliai.com/">castilliai.com</a>.</p>
  <h2>Get in touch</h2>
  <p>Email <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>. Please do not email medical records until we have agreed how they will be sent. If you want to start a Stage 1 review, you can <a href="{STRIPE_STAGE1}">pay the £349 fee</a> or <a href="/eligibility/">take the free check</a> first.</p>
 </div>
</section>"""
    return page(
        "/about/",
        "About Daniel Wyatt and the CHC Appeals Navigator service",
        "Daniel Wyatt, trading as CastilliAI, explains who runs CHC Appeals Navigator, his background, and how every guide is human-checked.",
        "About Daniel Wyatt and this service",
        body,
    )


def how_page() -> str:
    body = f"""<section class="legal">
 <div class="wrap prose">
  {crumb(("/how-it-works/", "How it works"))}
  <h1>How we prepare a funding appeal</h1>
  {byline("page")}
  <p>The official path, if you disagree with an eligibility decision, is to ask your integrated care board for a local resolution review, and then, if needed, to ask NHS England for an independent review. We do not replace that process. We help you prepare for it, one paid stage at a time.</p>
  <h2>1. Start with a free check, if you want one</h2>
  <p>The <a href="/eligibility/">10-question check</a> is a simple weighted questionnaire. It is not the official NHS Checklist or Decision Support Tool, and it is not a decision on eligibility. It is only there to help you judge whether a closer look is worthwhile.</p>
  <h2>2. Stage 1 — evidence review and a written verdict</h2>
  <p>For a fixed £349 you send the records you already have: care notes, GP and hospital letters, the Checklist or DST if you have it, and the decision letter. We map what is there to the 12 Decision Support Tool domains and send you a written report with a Yes, No or Maybe verdict, after I have reviewed it.</p>
  <p>If the verdict is No, you stop, with nothing more to pay. If it is Yes or Maybe, you decide whether to go on to Stage 2.</p>
  <h2>3. Stage 2 — the local resolution pack</h2>
  <p>Local resolution is the ICB's own review process. The National Framework requires every ICB to have one, and says concerns should first be discussed clearly, with a written note of that discussion. Stage 2 is the pack for that process: a letter, commentary on the DST, and preparation for a meeting if one is offered.</p>
  <p>If your Stage 1 verdict was Maybe, you instruct Stage 2, and the ICB still upholds the refusal, we refund 25% of the Stage 2 fee when we have the final written decision.</p>
  <h2>4. Later stages, only if you want them</h2>
  <p>If you remain dissatisfied after local resolution, you can apply to NHS England for an independent review. Stage 3 is preparation and representation for that review. Stage 4 is help with a complaint to the Parliamentary and Health Service Ombudsman. Stage 5 is a look at a past period of care, including after a death.</p>
  <p>You are not obliged to buy any later stage. Fees, cancellation and the 14-day cooling-off period are set out in the <a href="/pricing/">pricing page</a> and the <a href="/terms/">terms</a>.</p>
  <div class="cta-row">
   <a class="btn btn-primary" href="{STRIPE_STAGE1}">Start Stage 1 — £349</a>
   <a class="btn btn-secondary" href="/eligibility/">Free check</a>
  </div>
 </div>
</section>"""
    return page(
        "/how-it-works/",
        "How we prepare an NHS Continuing Healthcare funding appeal",
        "From a free check to a written Stage 1 verdict and later appeal stages. Fixed fees, a 14-day cooling-off period, and no lock-in.",
        "How we prepare a funding appeal",
        body,
    )


def pricing_page() -> str:
    cards = []
    for s in STAGES:
        feat = ""
        if s.get("note"):
            feat = f'<p class="small">{esc(s["note"])}</p>'
        cls = "price-card featured" if s["primary"] else "price-card"
        btn = "btn btn-primary" if s["primary"] else "btn btn-secondary"
        cards.append(
            f"""<article class="{cls}">
   <h2>{esc(s["name"])}</h2>
   <p class="amt">{esc(s["price"])}</p>
   <p class="period">{esc(s["period"])}</p>
   <p>{esc(s["blurb"])}</p>
   {feat}
   <a class="{btn}" href="{s["href"]}">{esc(s["cta"])}</a>
  </article>"""
        )
    body = f"""<section>
 <div class="wrap">
  {crumb(("/pricing/", "Prices"))}
  <h1>Pay per stage, and stop whenever you want</h1>
  {byline("page")}
  <p class="lead">Every stage is optional after the one you have bought. There is a 14-day cooling-off period on paid stages, as required for most distance contracts. Payment plans via GoCardless, where they are offered, are subject to status.</p>
  <div class="prices-grid">
  {chr(10).join(cards)}
  </div>
  <div class="note">
   <p><strong>VAT.</strong> All prices on this page are fixed fees and no VAT is charged, because we are not VAT registered.</p>
   <p>Stages 3, 4 and 5 are instructed by email because we do not currently have a separate payment link for those fees. Email <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> and we will tell you how to pay before work starts.</p>
   <p>Nobody can guarantee that an appeal will succeed. Eligibility is decided by the ICB, and by NHS England if the case goes to an independent review.</p>
  </div>

  <div class="compare">
   <h2>Stage 1 compared with Beacon&rsquo;s Expert Analysis</h2>
   <p>Our Stage 1 evidence review and written Yes / No / Maybe verdict is a fixed £349, with no VAT charged (we are not VAT registered). Beacon&rsquo;s Expert Analysis Service, a written review after a “not eligible” decision plus a follow-up consultation, is published at £1,600 plus VAT (£1,920 including VAT at 20%). The two services have a similar purpose but are not identical in scope: Beacon&rsquo;s published Expert Analysis is based on the Decision Support Tool and decision paperwork, with additional documents charged at their hourly rate; our Stage 1 reviews the records you upload and includes 12-domain mapping and a verdict. Families can also get free initial information and advice from Beacon&rsquo;s <a href="https://beaconchc.co.uk/how-we-can-help/free-information-and-advice-on-nhs-continuing-healthcare/">NHS England-funded advice service</a>.</p>
   <p class="small">Sources: <a href="https://beaconchc.co.uk/about-us/our-fees/">Beacon, Our Fees</a> and this page, accessed 24 November 2026 (Europe/London). This is a comparison of those two published fixed fees only, not a general claim that we are cheaper than Beacon.</p>
  </div>
 </div>
</section>"""
    return page(
        "/pricing/",
        "Pay-per-stage prices for Continuing Healthcare appeal help",
        "Stage 1 evidence review is £349. Later stages are optional. Pay as you go, stop any time, and use a 14-day cooling-off period.",
        "Pay per stage, and stop whenever you want",
        body,
    )


def eligibility_page() -> str:
    body = f"""<section>
 <div class="wrap quiz">
  {crumb(("/eligibility/", "Free check"))}
  <h1>Check your grounds for an appeal</h1>
  {byline("page")}
  <p>Answer ten questions about your relative's situation and the decision you have received. You will get a preliminary indication straight away. We do not ask for your name or email, and the answers stay in your browser.</p>
  <p class="notice">This check is not an official NHS Checklist or Decision Support Tool, and it is not legal or medical advice. Only the integrated care board can decide eligibility. The official process is described in the <a href="{GOVUK_LEAFLET}">GOV.UK public information leaflet</a>.</p>
  <div id="quiz"></div>
  <noscript><p>The check needs JavaScript. If you prefer not to use it, <a href="mailto:{CONTACT_EMAIL}">email us</a> or read the <a href="/guides/">guides</a> and <a href="/pricing/">prices</a> instead.</p></noscript>
  <script src="/assets/eligibility.js" defer></script>
 </div>
</section>"""
    return page(
        "/eligibility/",
        "Check your grounds for an NHS Continuing Healthcare appeal",
        "Answer ten questions about your relative's care and the decision letter. Get a preliminary indication, not an official NHS assessment.",
        "Check your grounds for an appeal",
        body,
    )


def faq_page() -> str:
    # HOME_FAQS last item in schema is plain "Read our privacy notice."
    # On this longer page, render all as plain text plus a privacy link in the last answer the same way as home for the first six.
    rendered = []
    for q, a in FAQ_PAIRS:
        html_a = esc(a)
        rendered.append(f"<details><summary>{esc(q)}</summary><div class=\"ans\"><p>{html_a}</p></div></details>")
    body = f"""<section class="legal">
 <div class="wrap" style="max-width:800px">
  {crumb(("/faq/", "FAQ"))}
  <h1>Questions families ask us</h1>
  {byline("page")}
  {chr(10).join(rendered)}
 </div>
</section>"""
    return page(
        "/faq/",
        "Answers to frequent NHS Continuing Healthcare appeal queries",
        "Answers about NHS Continuing Healthcare, the Decision Support Tool, time limits, our fees, and what we can and cannot do.",
        "Questions families ask us",
        body,
        extra_schema=[faq_schema(FAQ_PAIRS)],
    )



GUIDE_SOURCES_CORE = [
    ("National Framework for NHS Continuing Healthcare and NHS-funded Nursing Care (GOV.UK)", GOVUK_FRAMEWORK),
    ("NHS Continuing Healthcare Decision Support Tool guidance (GOV.UK)", GOVUK_DST),
    ("Public information leaflet: NHS continuing healthcare and NHS-funded nursing care (GOV.UK)", GOVUK_LEAFLET),
]


def guides_index() -> str:
    cards = [
        (
            "/guides/well-managed-needs/",
            "When well-managed needs still count",
            "What the 2022 National Framework says about needs that are being successfully managed, and how that can affect a DST score.",
        ),
        (
            "/guides/dst-domains/",
            "The 12 Decision Support Tool domains",
            "How the official tool records levels of need, and what the guidance says about a primary health need.",
        ),
        (
            "/guides/appeal-deadlines/",
            "Time limits for asking for a review",
            "How to ask your ICB for a local resolution review, and when NHS England can look at the case.",
        ),
        (
            "/guides/retrospective-claims/",
            "Reviews of past care fees",
            "If a past period of care was never properly assessed, you can ask the ICB to look at it, including after a death.",
        ),
    ]
    items = "\n  ".join(
        f'<a class="card" href="{href}"><h2>{esc(title)}</h2><p>{esc(blurb)}</p></a>'
        for href, title, blurb in cards
    )
    body = f"""<section>
 <div class="wrap" style="max-width:800px">
  {crumb(("/guides/", "Guides"))}
  <h1>Plain-English guides to the rules</h1>
  {byline("page")}
  <p>These notes are for families in England. They are based on the National Framework and the official Decision Support Tool guidance. They are not legal or medical advice, and they are not a substitute for reading your decision letter.</p>
  <div class="guide-list">
  {items}
  </div>
 </div>
</section>"""
    return page(
        "/guides/",
        "Plain-English guides to NHS Continuing Healthcare rules",
        "Plain-English notes on well-managed needs, the 12 DST domains, time limits for a review, and looking back at past care fees.",
        "Plain-English guides to the rules",
        body,
    )


def guide_well_managed() -> str:
    body = f"""<section class="legal">
 <div class="wrap prose">
  {crumb(("/guides/", "Guides"), ("", "Well-managed needs"))}
  <h1>When well-managed needs still count</h1>
  {byline()}
  <p>Families often read an eligibility letter that plays down a need because the person currently looks stable: the skin is intact, meals are being managed, or behaviour is settled with a particular routine. The National Framework does not allow a need to be set aside just because it is being successfully managed.</p>
  <h2>What the 2022 Framework actually says</h2>
  <p>The current National Framework (July 2022, later corrected) puts this in paragraphs 162 to 166, and states the same principle earlier in the document. The wording is:</p>
  <blockquote>The decision-making rationale should not marginalise a need just because it is successfully managed: well-managed needs are still needs. Only where the successful management of a healthcare need has permanently reduced or removed an ongoing need, such that the active management of this need is reduced or no longer required, will this have a bearing on NHS Continuing Healthcare eligibility.</blockquote>
  <p>Some older commentary, including earlier versions of our own draft notes, cited paragraphs 142 to 144 for this point. Those numbers come from an earlier edition of the Framework. In the 2022 text, the well-managed needs paragraphs are 162 to 166. If you are writing to the ICB, quote the current wording and paragraph numbers.</p>
  <h2>A necessary caution</h2>
  <p>The official Decision Support Tool guidance repeats the same principle, then adds an important limit. It is not meant to be applied as if routine medication or everyday care were simply not there. For example, needs managed with medication may belong in the drug therapies and medication domain, and it would not be right to score the skin domain as if good continence care was not being provided.</p>
  <p>In other words: do not ignore a need because it is well managed; and do not invent a higher score by pretending that the care already being given does not exist. The question is what need is still there, and what skill, frequency and risk are involved in meeting it.</p>
  <h2>What this can mean in a review</h2>
  <p>If a domain was scored low only because a symptom is currently controlled, it is fair to ask the ICB to look again at the underlying need, the consequences if the intervention stopped or was delayed, and the evidence in the daily records. Care charts, incident logs and medication records are often more useful here than a general impression that the person “is settled”.</p>
  <p>This is general information. It does not mean a particular score is “unlawful”, and it does not decide eligibility. That remains a decision for the ICB, looking at the person's needs as a whole, including their nature, intensity, complexity and unpredictability.</p>
  <p>Related guides: <a href="/guides/dst-domains/">the 12 DST domains</a> and <a href="/guides/appeal-deadlines/">time limits for a review</a>.</p>
  {sources(GUIDE_SOURCES_CORE)}
 </div>
</section>"""
    return page(
        "/guides/well-managed-needs/",
        "When well-managed needs still count in a CHC assessment",
        "What the 2022 National Framework says about well-managed needs, including paragraphs 162 to 166, and how that can affect a DST score.",
        "When well-managed needs still count",
        body,
        article=True,
    )


def guide_dst() -> str:
    body = f"""<section class="legal">
 <div class="wrap prose">
  {crumb(("/guides/", "Guides"), ("", "DST domains"))}
  <h1>The 12 Decision Support Tool domains</h1>
  {byline()}
  <p>The Decision Support Tool (DST) is the national document used in England to help practitioners apply the National Framework. It is not itself the assessment of needs, and it does not, on its own, decide eligibility. A multidisciplinary team completes it after a comprehensive assessment, and the integrated care board decides whether the person has a primary health need.</p>
  <h2>The twelve domains</h2>
  <p>The official tool groups needs into twelve domains:</p>
  <ol>
   <li>Behaviour</li>
   <li>Cognition</li>
   <li>Psychological and emotional needs</li>
   <li>Communication</li>
   <li>Mobility</li>
   <li>Nutrition (food and drink)</li>
   <li>Continence</li>
   <li>Skin (including tissue viability)</li>
   <li>Breathing</li>
   <li>Drug therapies and medication</li>
   <li>Altered states of consciousness</li>
   <li>Other significant care needs</li>
  </ol>
  <p>Each domain is recorded at a level such as no needs, low, moderate, high, severe or, in some domains only, priority. Not every domain has a priority level. The official guidance says that is because needs in some domains are not treated as enough, on their own, to indicate a primary health need.</p>
  <p>The twelfth domain is for significant needs that are not covered by the first eleven. It can be scored from low to severe. It should not be used to tilt the overall decision unfairly.</p>
  <h2>What the guidance says about a clear recommendation</h2>
  <p>Official DST guidance says a clear recommendation of eligibility would be expected where there is:</p>
  <ul>
   <li>a Priority level in any one of the four domains that have that level: breathing, behaviour, drug therapies and medication, and altered states of consciousness; or</li>
   <li>two or more Severe levels across the domains.</li>
  </ul>
  <p>It also says that the following may indicate a primary health need, depending on the combination of needs: a Severe level combined with needs in several other domains, or several domains with high and/or moderate needs.</p>
  <p>That is not a guarantee. The ICB still has to look at the person's needs as a whole, including their nature, intensity, complexity and unpredictability, and at the legal limits of what a local authority can provide. A diagnosis, or a word such as “severe” in a medical note, does not automatically mean the matching DST level should be selected. It is the descriptor that most closely fits the need and the support required that should be used.</p>
  <h2>Well-managed needs in the DST</h2>
  <p>The same official guidance repeats that well-managed needs are still needs, and points to paragraphs 162 to 166 of the National Framework. See our note on <a href="/guides/well-managed-needs/">well-managed needs</a>.</p>
  <p>Related: <a href="/guides/appeal-deadlines/">asking for a review</a> and <a href="/how-it-works/">how our Stage 1 review works</a>.</p>
  {sources(GUIDE_SOURCES_CORE)}
 </div>
</section>"""
    return page(
        "/guides/dst-domains/",
        "Decision Support Tool domains for Continuing Healthcare",
        "The 12 Decision Support Tool domains, how levels of need are recorded, and what the official guidance says about a primary health need.",
        "The 12 Decision Support Tool domains",
        body,
        article=True,
    )


def guide_deadlines() -> str:
    body = f"""<section class="legal">
 <div class="wrap prose">
  {crumb(("/guides/", "Guides"), ("", "Time limits"))}
  <h1>Time limits for asking the ICB to review a decision</h1>
  {byline()}
  <p>If you disagree with an eligibility decision after a full assessment, you can ask the integrated care board to review the case through its local resolution process. If you disagree with a Checklist decision not to go on to a full assessment, you can ask the ICB to look at that again. This is set out in the GOV.UK public information leaflet.</p>
  <h2>What the letter should tell you</h2>
  <p>The National Framework says the ICB must tell you the decision, the reasons, and the arrangements and timescales for asking for a review. Read the letter carefully and keep the envelope or email if you have them. The date on the written decision is the date most ICB processes use.</p>
  <h2>The common 6-month period</h2>
  <p>The Framework itself tells ICBs to publish a fair process with timescales, and points to NHS England for further operational guidance. In practice, ICB procedures across England commonly ask that a local resolution request is made within 6 months of the written decision. That 6-month figure also appears in older national timeframes introduced for these reviews.</p>
  <p>Those same timeframes, and many ICB policies, allow a later request where there is a good reason for the delay and the relevant records can still be obtained. So it is not accurate to say that the file is always closed for good on the day the sixth month ends. It is accurate to say you should not wait if you can help it, and that you should follow the instructions on your letter.</p>
  <h2>What “local resolution” involves</h2>
  <p>Every ICB must have a published local resolution process. The Framework says concerns should first be discussed clearly between the ICB and the family, with a written summary for both sides, and that the process should be fair and timely. Many ICBs aim to finish a local review within three months of a complete request, though that can take longer if records are delayed.</p>
  <p>Our Stage 2 service is a Local Resolution pack for this first formal appeal after a refusal. It does not replace the ICB's process, and we cannot guarantee the outcome.</p>
  <h2>If you still disagree: NHS England and the Ombudsman</h2>
  <p>If local resolution does not resolve the matter, you can apply to NHS England for an independent review of the eligibility decision, or of the procedure the ICB followed. NHS England may first ask the ICB to try further local resolution. NHS England's public guide explains how to apply; ICBs often say a request should be made within 6 months of the local resolution outcome letter, and NHS England asks for its application form back within six weeks.</p>
  <p>An independent review panel makes a recommendation. If you remain dissatisfied after that review, you can complain to the Parliamentary and Health Service Ombudsman. The Ombudsman process is about the NHS, not about this advocacy service.</p>
  <p>Related: <a href="/guides/retrospective-claims/">reviews of past care fees</a> and <a href="/how-it-works/">how we prepare a case</a>.</p>
  {sources(GUIDE_SOURCES_CORE + [
      ("NHS England, NHS Continuing Healthcare: independent review process (PDF)", NHSE_IR),
  ])}
 </div>
</section>"""
    return page(
        "/guides/appeal-deadlines/",
        "Time limits for asking the ICB to review a CHC decision",
        "How to ask your ICB for a local resolution review, when NHS England can look at the case, and why you should not ignore the letter's dates.",
        "Time limits for asking the ICB to review a decision",
        body,
        article=True,
    )


def guide_retrospective() -> str:
    body = f"""<section class="legal">
 <div class="wrap prose">
  {crumb(("/guides/", "Guides"), ("", "Past care fees"))}
  <h1>Asking for a review of past care fees</h1>
  {byline()}
  <p>Some families only hear about NHS Continuing Healthcare after a relative has already been paying for a care home, or after they have died. A past period of care can still be looked at, particularly where there was no proper CHC assessment at the time, or where you believe an earlier decision was wrong.</p>
  <h2>Who can ask</h2>
  <p>A person who holds the proper authority, including an executor or an attorney where that is relevant, can ask the ICB to consider a past period. A death does not, by itself, end the possibility of a review of a period when the person was alive and may have had a primary health need.</p>
  <h2>What can happen if a primary health need is later found</h2>
  <p>If the ICB later decides that the person was eligible for a past period, it may need to refund care fees that should have been arranged and funded by the NHS for that period. The National Framework includes refunds guidance for cases where responsibility between the NHS and a local authority is sorted out late. The exact amount, the period covered, and any additional redress depend on the facts and the guidance that applies to that case. It would not be accurate to say that every estate is automatically owed a fixed sum, or that interest is always added in a particular way.</p>
  <h2>FNC is not the same as full CHC</h2>
  <p>NHS-funded nursing care (FNC) is a weekly contribution towards registered nursing in a nursing home. It is paid at a national flat rate. From 1 April 2026 the standard rate is £267.68 a week (a higher rate applies only to a closed group of people who were already on the old high band before 1 October 2007). Full CHC, if awarded, covers the whole agreed care package, including accommodation, and is not means-tested.</p>
  <p>You should normally be assessed for CHC before an FNC decision is made. If you are only being offered FNC, or you are asked to treat FNC as a settlement of a wider claim, it is worth checking that a proper CHC assessment was done and that you understand what you are being offered before you accept it.</p>
  <h2>Evidence for a past period</h2>
  <p>A retrospective review has to work from records rather than a new face-to-face assessment: care home notes, GP records, hospital admissions, medication charts and any earlier Checklist or DST. Homes and GP practices keep records for a limited time, so it is better to ask sooner rather than later. Any time limits that apply to your situation should be checked with the ICB, and you should not assume that a delay always makes a review impossible, or that it never matters.</p>
  <p>Our Stage 5 service is a paid review of a past period, including after a death. The fee is £1,499 plus 8% of any recovery, with no VAT charged. It is not a guarantee of a refund.</p>
  <p>Related: <a href="/guides/appeal-deadlines/">time limits for a current decision</a> and <a href="/pricing/">prices</a>.</p>
  {sources(GUIDE_SOURCES_CORE + [
      ("NHS-funded nursing care rates (NHS.uk)", NHS_FNC),
      ("NHS continuing healthcare (NHS.uk)", NHS_CHC),
  ])}
 </div>
</section>"""
    return page(
        "/guides/retrospective-claims/",
        "Retrospective Continuing Healthcare reviews of past care fees",
        "If a past period of care was never properly assessed for Continuing Healthcare, you can ask the ICB to look at it, including after a death.",
        "Asking for a review of past care fees",
        body,
        article=True,
    )


def privacy_page() -> str:
    body = f"""<section class="legal">
 <div class="wrap prose">
  {crumb(("/privacy/", "Privacy notice"))}
  <h1>How we use personal information</h1>
  {byline("page")}
  <h2>Who we are</h2>
  <p>CHC Appeals Navigator is a service of {esc(LEGAL_NAME)}. We are the controller of the personal information you give us. Contact: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>
  <h2>This website</h2>
  <p>The public pages of this site are a plain information site. They set no cookies and run no analytics or advertising trackers. The free eligibility check runs in your browser and does not send your answers to us. Our host (GitHub Pages) may log technical data such as IP addresses for security.</p>
  <h2>What we collect when you use the paid service</h2>
  <ul>
   <li><strong>Contact and payment details:</strong> your name, email, phone and billing details. Card payments are handled by Stripe; we do not see or store your full card number.</li>
   <li><strong>Eligibility check answers:</strong> only if you later choose to send them to us. The on-site check itself does not transmit answers.</li>
   <li><strong>Case records:</strong> documents you upload about your relative, such as care notes, GP and hospital records, assessments and decision letters. This is health information, which is special category data under UK GDPR.</li>
  </ul>
  <h2>Why we use it and our lawful basis</h2>
  <ul>
   <li>To provide the stage you have bought: contract.</li>
   <li>To process health information about your relative: your explicit consent, and where relevant the establishment, exercise or defence of legal claims. You should only upload a relative's records where you are entitled to act for them, for example with their agreement or as their attorney or deputy.</li>
   <li>To keep accounting records: legal obligation.</li>
  </ul>
  <h2>Who we share it with</h2>
  <p>We share information only as needed to run the service: Stripe (payments), our hosting and storage providers, and, when you instruct us, the ICB, NHS England or the Ombudsman as part of your appeal. We never sell your information or use your family's records to train public AI models.</p>
  <h2>How long we keep it</h2>
  <p>We keep case records only as long as needed for your case and any follow-on stages, and accounting records for as long as the law requires. You can ask us to delete your case records at any time, subject to those legal requirements.</p>
  <h2>Your rights</h2>
  <p>You can ask for a copy of your information, ask us to correct or delete it, object to or restrict how we use it, and withdraw consent at any time. Email <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>. If you are unhappy with how we handle your information, you can complain to the <a href="https://ico.org.uk/make-a-complaint/">Information Commissioner's Office</a>.</p>
  <p><a href="/">← Back to CHC Appeals Navigator</a></p>
 </div>
</section>"""
    return page(
        "/privacy/",
        "How we use personal information at CHC Appeals Navigator",
        "How CHC Appeals Navigator (Daniel Wyatt t/a CastilliAI) uses personal and health information, and how to ask us to delete records.",
        "How we use personal information",
        body,
    )


def terms_page() -> str:
    body = f"""<section class="legal">
 <div class="wrap prose">
  {crumb(("/terms/", "Terms"))}
  <h1>Client terms and conditions</h1>
  {byline("page")}
  <p>These terms apply when you buy a stage of {esc(NAME)} from {esc(LEGAL_NAME)}.</p>
  <h2>What this service is</h2>
  <p>{esc(DISCLAIMER)} Reports and appeal packs are case preparation under the National Framework. They are not a formal legal opinion and not a medical diagnosis. Eligibility is decided by the ICB, and by NHS England if a case goes to an independent review. Nobody can guarantee that an appeal will be granted.</p>
  <h2>Fees and VAT</h2>
  <p>Fees are as published on the <a href="/pricing/">pricing page</a>: Stage 0 is free; Stage 1 is £349; Stage 2 is £799; Stage 3 is £1,499; Stage 4 is £399; Stage 5 is £1,499 plus 8% of any recovery. These are fixed prices and no VAT is charged, because we are not VAT registered. You are not obliged to buy a later stage. Payment plans via GoCardless, where offered, are subject to status.</p>
  <h2>14-day cooling-off period</h2>
  <p>For a distance contract, you have a 14-day right to cancel under the Consumer Contracts (Information, Cancellation and Additional Charges) Regulations 2013. If you ask us to start work during that period and then cancel, we may charge for the work already done, up to the stage fee.</p>
  <h2>Stage 2 refund if Stage 1 was Maybe</h2>
  <p>If the Stage 1 report gives a Maybe verdict, you instruct Stage 2, and the ICB's Local Resolution process upholds the refusal, we will refund 25% of the Stage 2 fee when we have received the final written determination.</p>
  <h2>Your responsibilities</h2>
  <p>You must be entitled to act for the person whose records you send, and the information you give us must be accurate so far as you know. You remain responsible for meeting any ICB or NHS England deadlines. We are not a law firm and cannot help with litigation.</p>
  <h2>Contact</h2>
  <p>Email <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>. The <a href="/complaints/">complaints procedure</a> and <a href="/privacy/">privacy notice</a> also form part of how we work with you.</p>
 </div>
</section>"""
    return page(
        "/terms/",
        "Client terms and conditions for CHC Appeals Navigator work",
        "The terms on which Daniel Wyatt t/a CastilliAI provides CHC Appeals Navigator services, including fees, refunds and cancellation.",
        "Client terms and conditions",
        body,
    )


def complaints_page() -> str:
    body = f"""<section class="legal">
 <div class="wrap prose">
  {crumb(("/complaints/", "Complaints"))}
  <h1>How to complain</h1>
  {byline("page")}
  <p>If you are unhappy with CHC Appeals Navigator, please tell {esc(AUTHOR)} so that it can be put right. This service is run by him personally. There is no other staff member to escalate to.</p>
  <h2>Stage 1 — tell us</h2>
  <p>Email <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> with the word “Complaint” in the subject line, and a short account of what went wrong. We will acknowledge the email within two working days and aim to give you a written reply within ten working days.</p>
  <h2>Stage 2 — a second look</h2>
  <p>If you are not satisfied with that reply, say so in writing and ask for the complaint to be looked at again. You will receive a further written response within 14 working days.</p>
  <h2>If you are still unhappy</h2>
  <p>We are not a law firm, an NHS body or a regulated claims business, so the Legal Ombudsman and the Parliamentary and Health Service Ombudsman do not deal with complaints about this service. Depending on the issue, you may:</p>
  <ul>
   <li>complain to the <a href="https://ico.org.uk/make-a-complaint/">Information Commissioner's Office</a> about the way personal information has been handled;</li>
   <li>get independent consumer advice, for example from Citizens Advice, or consider a claim in the small claims court for a contract dispute.</li>
  </ul>
  <p>If your concern is about an NHS eligibility decision rather than about our work, use the ICB's process and, where relevant, NHS England or the Parliamentary and Health Service Ombudsman. Our <a href="/guides/appeal-deadlines/">time limits guide</a> explains that route.</p>
 </div>
</section>"""
    return page(
        "/complaints/",
        "Our complaints procedure at CHC Appeals Navigator explained",
        "How to complain about CHC Appeals Navigator, how quickly we will reply, and what you can do if you are still unhappy.",
        "How to complain",
        body,
    )


def write_file(path: str, html: str) -> None:
    if path == "/":
        dest = ROOT / "index.html"
    else:
        dest = ROOT / path.lstrip("/") / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")
    print("wrote", dest.relative_to(ROOT), "chars", len(html))


def write_sitemap(paths: list[str]) -> None:
    urls = []
    for p in paths:
        loc = BASE + p
        urls.append(f"<url><loc>{loc}</loc><lastmod>{TODAY}</lastmod></url>")
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")
    print("wrote sitemap.xml", len(paths), "urls")


def main() -> None:
    pages = [
        ("/", home_page),
        ("/about/", about_page),
        ("/how-it-works/", how_page),
        ("/pricing/", pricing_page),
        ("/eligibility/", eligibility_page),
        ("/faq/", faq_page),
        ("/guides/", guides_index),
        ("/guides/well-managed-needs/", guide_well_managed),
        ("/guides/dst-domains/", guide_dst),
        ("/guides/appeal-deadlines/", guide_deadlines),
        ("/guides/retrospective-claims/", guide_retrospective),
        ("/privacy/", privacy_page),
        ("/terms/", terms_page),
        ("/complaints/", complaints_page),
    ]
    for path, fn in pages:
        write_file(path, fn())
    write_sitemap([p for p, _ in pages])
    # Keep robots.txt as an allow-all file pointing at the sitemap.
    robots = "User-agent: *\nAllow: /\nSitemap: https://chc.castilliai.com/sitemap.xml\n"
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")
    print("build complete")


if __name__ == "__main__":
    main()
