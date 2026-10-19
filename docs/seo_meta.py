#!/usr/bin/env python3
"""Inject SEO metadata into docs/index.html.

Two places, because the bundler swaps the entire document
(document.documentElement.replaceWith) on load:

  1. the __bundler/template <head>  -> this is the DOM crawlers actually index
  2. the wrapper <head>              -> what a non-JS scraper reads first

Run from the repo root:  python3 docs/seo_meta.py
"""
import json
import re
from pathlib import Path

DOC = Path(__file__).resolve().parent / "index.html"

CANONICAL = "https://sakhadib.github.io/literal-lock-in/"
IMAGE = CANONICAL + "og.png"
ARXIV = "https://arxiv.org/abs/2610.22526"
DOI = "https://doi.org/10.48550/arXiv.2610.22526"
GH = "https://github.com/sakhadib/literal-lock-in"

TITLE = "Literal Lock-In: Literal Attraction in Bengali Idioms"
PAGE_TITLE = (
    "Literal Lock-In: How Test Language Shifts Literal Attraction in "
    "Typed Decision Models on Bengali Idioms"
)
DESCRIPTION = (
    "Decision models emit no text, only scores. On Bengali idioms, putting an "
    "idiom's own literal gloss into the option list captures them 1.9 to 6.4 "
    "times more in Bengali than in English, and their confidence inverts. "
    "arXiv:2610.22526."
)
KEYWORDS = (
    "decision models, typed output, option scoring, multiple choice, literal "
    "attraction, Bengali idioms, Bangla NLP, figurative language, calibration, "
    "selective prediction, LLM evaluation, cross-lingual evaluation, low-resource "
    "languages, guardrails, model auditing"
)

LD = {
    "@context": "https://schema.org",
    "@type": "ScholarlyArticle",
    "headline": PAGE_TITLE,
    "alternativeHeadline": "Literal Lock-In",
    "name": PAGE_TITLE,
    "description": DESCRIPTION,
    "url": CANONICAL,
    "datePublished": "2026-10-15",
    "inLanguage": "en",
    "isAccessibleForFree": True,
    "genre": "Research paper",
    "creativeWorkStatus": "Under review",
    "license": "https://creativecommons.org/licenses/by-sa/4.0/",
    "keywords": KEYWORDS,
    "identifier": ["arXiv:2610.22526", DOI, "doi:10.48550/arXiv.2610.22526"],
    "sameAs": [ARXIV, GH, DOI],
    "citation": [
        "Adib Sakhawat and Syed Rifat Raiyan. Literal Lock-In: How Test Language "
        "Shifts Literal Attraction in Typed Decision Models on Bengali Idioms. "
        "arXiv:2610.22526 [cs.CL], 2026."
    ],
    "author": [
        {
            "@type": "Person",
            "name": "Adib Sakhawat",
            "affiliation": {
                "@type": "CollegeOrUniversity",
                "name": "Islamic University of Technology",
            },
        },
        {
            "@type": "Person",
            "name": "Syed Rifat Raiyan",
            "affiliation": {
                "@type": "CollegeOrUniversity",
                "name": "Islamic University of Technology",
            },
        },
    ],
    "publisher": {"@type": "Organization", "name": "arXiv", "sameAs": "https://arxiv.org"},
    "about": [
        {"@type": "Thing", "name": "Typed decision models"},
        {"@type": "Thing", "name": "Bengali idioms"},
        {"@type": "Thing", "name": "Literal attraction rate"},
        {"@type": "Thing", "name": "Calibration of language models"},
    ],
}


def meta(*attrs):
    """One <meta> tag per 4 args: name, value, name, value."""
    assert len(attrs) % 4 == 0, "meta() takes name/value pairs"
    out = ""
    for i in range(0, len(attrs), 4):
        out += (
            f'  <meta {attrs[i]}="{attrs[i + 1]}" '
            f'{attrs[i + 2]}="{attrs[i + 3]}">\n'
        )
    return out


HEAD = f"""<title>{TITLE}</title>
{meta(
    "name", "description", "content", DESCRIPTION,
    "name", "keywords", "content", KEYWORDS,
    "name", "author", "content", "Adib Sakhawat, Syed Rifat Raiyan",
    "name", "robots", "content", "index, follow, max-image-preview:large, max-snippet:-1",
    "name", "twitter:card", "content", "summary_large_image",
    "name", "twitter:site", "content", "@sakhadib",
    "name", "twitter:creator", "content", "@sakhadib",
    "name", "twitter:title", "content", TITLE,
    "name", "twitter:description", "content", DESCRIPTION,
    "name", "twitter:image", "content", IMAGE,
    "property", "og:type", "content", "article",
    "property", "og:site_name", "content", "Literal Lock-In",
    "property", "og:title", "content", TITLE,
    "property", "og:description", "content", DESCRIPTION,
    "property", "og:url", "content", CANONICAL,
    "property", "og:image", "content", IMAGE,
    "property", "og:image:width", "content", "1200",
    "property", "og:image:height", "content", "630",
    "property", "og:image:alt", "content",
    "Literal Lock-In — literal attraction in Bengali idiom decision models",
    "property", "og:locale", "content", "en_US",
    "property", "article:published_time", "content", "2026-10-15T00:00:00Z",
    "property", "article:section", "content", "Computation and Language",
)}  <link rel="canonical" href="{CANONICAL}">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="og.png">
  <meta property="og:image:type" content="image/png">
"""

# noscript payload: real content for crawlers and scrapers that never run JS
NOSCRIPT = f"""  <noscript>
    <div style="max-width:760px;margin:0 auto;padding:56px 24px;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif;color:#1d1f20;">
      <h1 style="font-size:30px;line-height:1.2;margin:0 0 6px;">{TITLE}</h1>
      <p style="font-size:17px;color:#2c455d;margin:0 0 22px;">{PAGE_TITLE}</p>
      <p style="font-size:15px;color:#5c6b7a;margin:0 0 22px;">Adib Sakhawat &middot; Syed Rifat Raiyan &mdash; Islamic University of Technology</p>
      <p style="font-size:16px;line-height:1.6;margin:0 0 22px;">{DESCRIPTION}</p>
      <p style="font-size:16px;line-height:1.6;margin:0 0 22px;">
        A decision model returns a probability over exactly the options the caller
        supplies and emits no text, so there is nothing to chain-of-thought. This
        work audits three such models &mdash; an encoder scorer, a decoder scorer
        and a closed API &mdash; entirely through interventions on the option list,
        using expert-annotated Bengali idioms that carry both a gold figurative
        meaning and a gold literal gloss. Dropping the idiom's own literal gloss
        into the option list takes 66 to 96 percent of each arm's remaining
        Bengali errors. On one shared item set, every arm is 1.9 to 6.4 times more
        captured in Bengali than in the paired English entry, calibration degrades
        in all three arms, and on the open arms confidence inverts, so gating on it
        is worse than gating at random.
      </p>
      <p style="font-size:16px;line-height:1.6;margin:0 0 26px;">
        <a href="{ARXIV}">Preprint on arXiv</a> &middot;
        <a href="{GH}">Code and per-item data</a> &middot;
        <a href="{DOI}">DOI</a>
      </p>
      <p style="font-size:14px;color:#5c6b7a;">This page renders with JavaScript enabled.</p>
    </div>
  </noscript>
"""


def inject_template(src):
    """Insert the SEO head + JSON-LD into the bundled template."""
    m = re.search(r'(<script type="__bundler/template">\n)(.*?)(\n  </script>)', src, re.S)
    tpl = json.loads(m.group(2))

    anchor = '<meta name="viewport" content="width=device-width, initial-scale=1">'
    assert anchor in tpl, "viewport meta not found in template"
    assert "<meta name=\"description\"" not in tpl, "SEO head already present"
    head = HEAD + '  <script type="application/ld+json">\n'
    head += json.dumps(LD, ensure_ascii=False, indent=2) + "\n  </script>\n"
    tpl = tpl.replace(anchor, anchor + "\n" + head, 1)

    # keep the live document title in step with the static one
    tpl = tpl.replace(
        "<title>Literal Lock-In — Bengali idioms and typed decision models</title>",
        f"<title>{TITLE}</title>",
    )
    return src[: m.start(2)] + json.dumps(tpl, ensure_ascii=False) + src[m.end(2) :]


def inject_wrapper(src):
    """SEO head + noscript fallback in the pre-hydration shell."""
    assert 'name="description"' not in src, "wrapper SEO already present"
    head = HEAD + NOSCRIPT
    head = head.replace('href="favicon.svg"', f'href="{CANONICAL}favicon.svg"')
    head = head.replace('href="og.png"', f'href="{CANONICAL}og.png"')
    old = "  <title>Literal Lock-In — Bengali idioms and typed decision models</title>"
    out = src.replace(old, head.rstrip("\n"), 1)
    assert out != src, "wrapper title not replaced"
    return out


def main():
    src = DOC.read_text(encoding="utf-8")
    out = inject_wrapper(inject_template(src))
    DOC.write_text(out, encoding="utf-8")

    # verify both landed and both JSON blobs still parse
    tpl = json.loads(
        re.search(r'<script type="__bundler/template">\n(.*?)\n  </script>', out, re.S).group(1)
    )
    ld = re.search(r'<script type="application/ld\+json">\n(.*?)\n  </script>', tpl, re.S)
    ld_data = json.loads(ld.group(1))
    assert ld_data["@type"] == "ScholarlyArticle"
    assert "{{" not in ld.group(1), "unresolved template token inside JSON-LD"
    print(f"template: {len(tpl)} chars, description tags: {tpl.count('name=\"description\"')}")
    print(f"wrapper : description tags: {out.count('name=\"description\"')}")
    print(f"canonical: {out.count(CANONICAL)} refs, arxiv id: {out.count('2610.22526')}")


if __name__ == "__main__":
    main()