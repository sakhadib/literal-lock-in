#!/usr/bin/env python3
"""Render docs/index.html — a static, semantic page.

Run from the repo root:  python3 docs/build_site.py

The previous site shipped as a single-file runtime bundle: a base64 manifest, a
React/Babel bundle, Plotly, and a templating layer that filled the markup in
after load. Nothing existed for a crawler that does not execute JavaScript, and
one stray `</script>` inside the embedded JSON was enough to break the page
outright.

This build emits plain HTML instead:

  src/template.html  the same markup, loops and placeholders expanded here
  src/site.css       the same design tokens and component classes
  src/charts.py      the eight Plotly figures, drawn as inline SVG
  src/app.js         vanilla JS for the toggles, cycles and reveal animation

Charts carry their values as SVG geometry and <title>, so every number in the
paper is in the DOM without JavaScript.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))
import charts as CH  # noqa: E402

SRC = HERE / "src"
OUT = HERE / "index.html"

MODELS = [
    {"name": "Laya-ml", "mk": "●", "color": "var(--color-accent-800)"},
    {"name": "Lod-lille", "mk": "■", "color": "var(--color-accent-500)"},
    {"name": "Jev-1.13", "mk": "▲", "color": "var(--color-neutral-500)"},
]

FAM = {
    "D-RAND": {"d": "Other idioms’ glosses, drawn at random.", "s": ["rand", "rand", "rand"]},
    "D-SURF": {"d": "Glosses sharing surface tokens with the gold.", "s": ["surf", "surf", "surf"]},
    "D-SEM": {"d": "Glosses from idioms sharing semantic tags.", "s": ["sem", "sem", "sem"]},
    "D-LIT": {"d": "One distractor replaced by the idiom’s own expert literal gloss.",
              "s": ["lit", "rand", "rand"]},
    "D-HARD": {"d": "All three pressures at once: literal, surface and semantic.",
               "s": ["lit", "surf", "sem"]},
}
SLOT = {
    "gold": {"t": "Gold figurative meaning", "tag": "gold"},
    "rand": {"t": "Random idiom’s gloss", "tag": "random"},
    "surf": {"t": "Gloss sharing surface tokens", "tag": "surface"},
    "sem": {"t": "Gloss sharing a semantic tag", "tag": "tag"},
    "lit": {"t": "The idiom’s own literal gloss", "tag": "literal"},
}
ARROW = "↑"
ON_BG, ON_FG = "var(--color-accent-900)", "#ffffff"
OFF_BG, OFF_FG = "transparent", "var(--color-text)"

BIB = """@misc{sakhawat2026literallockintestlanguage,
      title={Literal Lock-In: How Test Language Shifts Literal Attraction in Typed Decision Models on Bengali Idioms},
      author={Adib Sakhawat and Syed Rifat Raiyan},
      year={2026},
      eprint={2610.22526},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2610.22526},
}"""

CANONICAL = "https://sakhadib.github.io/literal-lock-in/"
ARXIV = "https://arxiv.org/abs/2610.22526"
DOI = "https://doi.org/10.48550/arXiv.2610.22526"
GH = "https://github.com/sakhadib/literal-lock-in"
TITLE = "Literal Lock-In: Literal Attraction in Bengali Idioms"
FULL_TITLE = ("Literal Lock-In: How Test Language Shifts Literal Attraction in "
              "Typed Decision Models on Bengali Idioms")
DESCRIPTION = (
    "Decision models emit no text, only scores. On Bengali idioms, putting an "
    "idiom's own literal gloss into the option list captures them 1.9 to 6.4 "
    "times more in Bengali than in English, and their confidence inverts. "
    "arXiv:2610.22526."
)
KEYWORDS = ("decision models, typed output, option scoring, multiple choice, literal attraction, "
            "Bengali idioms, Bangla NLP, figurative language, calibration, selective prediction, "
            "LLM evaluation, cross-lingual evaluation, low-resource languages, guardrails")


# ── the data the template asks for ────────────────────────────────────────────

def build_data():
    d = {}

    # hero: the model takes the words (initial state = Bengali)
    hero_p = ["1.00", "0.97", "0.36"]
    lar_bn = [0.731, 0.918, 0.304]
    lar_en = [0.379, 0.241, 0.047]
    rows = []
    for i, m in enumerate(MODELS):
        lit = True if i == 0 else True
        rows.append({**m, "left": "4%", "dir": "row",
                     "label": "literal · p = " + hero_p[i] if lit else "recovers"})
    d["heroRows"] = rows
    d["heroLar"] = [{**m, "v": f"{lar_bn[i]:.3f}"} for i, m in enumerate(MODELS)]
    d["heroBnBg"], d["heroBnFg"] = ON_BG, ON_FG
    d["heroEnBg"], d["heroEnFg"] = OFF_BG, OFF_FG

    d["findings"] = [
        {"n": "01 · Capture", "big": "66–96%",
         "text": "of each arm’s remaining Bengali errors are taken by the idiom’s own literal gloss."},
        {"n": "02 · Language", "big": "1.9–6.4×",
         "text": "more literal capture in Bengali than in English on the same paired entries, "
                 "in every arm."},
        {"n": "03 · Confidence", "big": "< random",
         "text": "On the open arms confidence inverts, so gating on it is worse than gating at random."},
        {"n": "04 · Control", "big": "0.82",
         "text": "mean confidence from the best-calibrated arm on a semantics-free list, where "
                 "accuracy is at chance."},
    ]

    stages = [
        ["01", "Corpus", "Bangla Bagdhara: 10,361 expert-annotated idioms with gold figurative "
                         "and literal glosses."],
        ["02", "Distractor family", "The sole manipulated variable. D-LIT and D-HARD inject the "
                                    "expert literal gloss."],
        ["03", "Item prompt", "Fixed typed question, k = 4 options, instruction and per-item order seed."],
        ["04", "Models", "Laya-ml, Lod-lille and Jev-1.13."],
        ["05", "Scoring", "Four-option probability vector, arg max and confidence. No generated text."],
        ["06", "Metrics", "Accuracy, LAR, ECE, AURC, agreement and order stability."],
    ]
    d["stages"] = [{"n": n, "title": t, "body": b,
                    "bg": ON_BG if i == 0 else "transparent",
                    "dot": 1 if i == 0 else 0,
                    "bar": "100%" if i == 0 else "0%"} for i, (n, t, b) in enumerate(stages)]

    d["families"] = [
        {"code": c,
         "bd": ON_BG if c == "D-LIT" else "var(--color-divider)",
         "bg": ON_BG if c == "D-LIT" else "transparent",
         "fg": ON_FG if c == "D-LIT" else "var(--color-text)"}
        for c in FAM
    ]
    d["famSlots"] = fam_slots("D-LIT")
    d["famDesc"] = FAM["D-LIT"]["d"]

    d["experiments"] = [
        {"id": "E1", "text": "The distractor family"}, {"id": "E2", "text": "The idiom’s surface form"},
        {"id": "E3", "text": "The idiom as a unit"}, {"id": "E4", "text": "The task language"},
        {"id": "E5", "text": "Nothing (derived from E1)"}, {"id": "E6", "text": "The option text"},
        {"id": "E7", "text": "The option order"},
    ]
    d["modelTable"] = [
        {"k": "backbone", "a": "mmBERT", "b": "Qwen3-0.6B", "c": "closed"},
        {"k": "scoring", "a": "marker", "b": "independent", "c": "unknown"},
        {"k": "parameters", "a": "322M", "b": "0.6B", "c": "n/a"},
        {"k": "items", "a": "8,876", "b": "888", "c": "8,761"},
        {"k": "latency", "a": "27.2 ms", "b": "86.1 ms", "c": "API"},
        {"k": "weights", "a": "open", "b": "open", "c": "closed"},
    ]

    fam_labels = ["random", "surface", "tag", "+ literal", "hard"]
    laya = [0.351, 0.339, 0.325, 0.136, 0.149]
    lod = [0.484, 0.412, 0.446, 0.066, 0.063]
    d["ladder"] = []
    for i, label in enumerate(fam_labels):
        bars = []
        for j, v in enumerate((laya[i], lod[i])):
            bars.append({"v": f"{v:.3f}", "color": MODELS[j]["color"],
                         "h": f"{v / 0.6 * 100:.1f}%", "delay": f"{i * 0.08 + j * 0.05}s", "op": 1})
        d["ladder"].append({
            "label": label,
            "lc": "var(--color-accent-800)" if i >= 3 else "var(--color-neutral-700)",
            "bg": "color-mix(in srgb, var(--color-accent-100) 70%, transparent)" if i >= 3 else "transparent",
            "bars": bars,
        })

    dec = [[0.136, 0.658, 0.206], [0.066, 0.885, 0.050]]
    seg_style = [["var(--color-accent-300)", "var(--color-accent-900)"],
                 ["var(--color-accent-800)", "#ffffff"],
                 ["var(--color-neutral-200)", "var(--color-neutral-800)"]]
    d["decomp"] = [
        {**m, "segs": [{"v": f"{v:.3f}" if v >= 0.1 else "", "w": f"{v * 100:.1f}%",
                        "bg": seg_style[j][0], "fg": seg_style[j][1]} for j, v in enumerate(dec[i])]}
        for i, m in enumerate(MODELS[:2])
    ]

    acc_bn = [0.127, 0.044, 0.536]
    acc_en = [0.417, 0.684, 0.926]
    d["matrix"] = [
        {"name": m["name"], "mk": m["mk"], "color": m["color"],
         "hatch": f"repeating-linear-gradient(45deg, {m['color']} 0 2px, transparent 2px 6px)",
         "bnV": f"{lar_bn[i]:.3f}", "enV": f"{lar_en[i]:.3f}",
         "bnW": f"{lar_bn[i] * 100:.1f}%", "enW": f"{lar_en[i] * 100:.1f}%"}
        for i, m in enumerate(MODELS)
    ]
    d["mxLarBg"], d["mxLarFg"] = ON_BG, ON_FG
    d["mxAccBg"], d["mxAccFg"] = OFF_BG, OFF_FG

    ok = [0.432, 0.453, 0.935]
    cap = [0.596, 0.787, 0.737]
    pos = lambda v: f"{(v - 0.3) / 0.7 * 100:.1f}%"  # noqa: E731
    d["confRows"] = [
        {**m, "ok": f"{ok[i]:.3f}", "cap": f"{cap[i]:.3f}",
         "okL": pos(ok[i]), "capL": pos(cap[i]), "lo": pos(min(ok[i], cap[i])),
         "span": f"{abs(ok[i] - cap[i]) / 0.7 * 100:.1f}%",
         "verdict": "more confident when captured" if cap[i] > ok[i] else "more confident when correct",
         "vc": "var(--color-accent-800)" if cap[i] > ok[i] else "var(--color-neutral-700)"}
        for i, m in enumerate(MODELS)
    ]

    ac, ar = [0.924, 0.989, 0.013], [0.849, 0.934, 0.069]
    d["aurc"] = [
        {**m, "hatch": f"repeating-linear-gradient(45deg, {m['color']} 0 2px, transparent 2px 6px)",
         "c": f"{ac[i]:.3f}", "r": f"{ar[i]:.3f}",
         "cW": f"{ac[i] * 100:.1f}%", "rW": f"{ar[i] * 100:.1f}%"}
        for i, m in enumerate(MODELS)
    ]

    real_opts = ["Gold figurative meaning"] + ["Random idiom’s gloss"] * 3
    d["o4Opts"] = [
        {"letter": "ABCD"[i], "real": r, "blank": f"meaning {i + 1}",
         "y1": "0%", "o1": 1, "y2": "100%", "o2": 0, "d": f"{i * 0.08}s"}
        for i, r in enumerate(real_opts)
    ]
    gaps = [0.250, 0.049, 0.561]
    d["o4"] = [{**m, "v": f"{gaps[i]:.3f}", "w": f"{gaps[i] / 0.6 * 100:.1f}%"}
               for i, m in enumerate(MODELS)]

    d["permN"] = 1
    d["permChips"] = perm_chips(0)

    ord_data = [["Answer changes across orderings", [0.837, 0.107, 0.133]],
                ["Perfectly stable items", [0.163, 0.893, 0.867]],
                ["Within-item range of p(gold)", [0.346, 0.029, 0.128]]]
    d["orderRows"] = [
        {"label": label,
         "bars": [{**m, "v": f"{vals[i]:.3f}", "w": f"{vals[i] * 100:.1f}%"}
                  for i, m in enumerate(MODELS)]}
        for label, vals in ord_data
    ]

    e3d = [["intact", 0.157, 0.072], ["word shuffle", 0.168, 0.044], ["reversed", 0.178, 0.056],
           ["delete 1 word", 0.158, 0.089], ["substitute 1 word", 0.162, 0.056],
           ["in carrier sentence", 0.237, 0.189]]
    d["e3"] = [
        {"label": label, "fw": 600 if i == 5 else 400,
         "bars": [{"v": f"{v:.3f}", "color": MODELS[j]["color"],
                   "w": f"calc({v / 0.4 * 100:.1f}% - 44px)", "delay": f"{i * 0.07 + j * 0.05}s"}
                  for j, v in enumerate((a, b))]}
        for i, (label, a, b) in enumerate(e3d)
    ]

    d["captures"] = [
        {"idiom": "কব্জা", "lit": "কব্জি বা হাতের আঁচড়ানো অংশ", "gold": "অবাঞ্ছিত অধিকার, প্রভাব"},
        {"idiom": "কাঠ", "lit": "কাঠ (wood)", "gold": "কঙ্কাল"},
        {"idiom": "চামচা", "lit": "চামচ (spoon)", "gold": "খোসামুদে; চাটুকার; তোষামুদে"},
        {"idiom": "গ্যাঁড়াকল", "lit": "গ্যাঁড়া (স্ক্রু বা ফাঁদের যন্ত্র) এবং কল",
         "gold": "লোক ঠকাবার কৌশল; বিপদ, ফাঁদ"},
    ]

    d["more"] = [
        {"sec": "§ 5.5 · Option side", "title": "Options are read lexically",
         "body": "Scrambling the words inside every option costs almost nothing: the three arms "
                 "retain 0.928, 0.944 and 1.005 of their above-chance signal."},
        {"sec": "§ 5.4 · Position", "title": "A 3.3× swing from position alone",
         "body": "With the gold placed uniformly, Laya-ml’s accuracy is 0.066 when the gold sits "
                 "in slot A against 0.215 in slot B. Lod-lille’s slot shares are near-uniform: "
                 "0.265 / 0.258 / 0.242 / 0.235."},
        {"sec": "E2 · Surface invariance", "title": "Synonymous forms, different answers",
         "body": "On expert-certified alternative surface forms with the same gold meaning, "
                 "answer agreement is only 0.657 (Laya-ml) and 0.677 (Lod-lille). About a third "
                 "of the time, the answer changes."},
        {"sec": "§ 5.6 · Construction cues", "title": "Lexical cues are real; neither carries the result",
         "body": "On the 2,480 items with no verbatim overlap and no Latin-script cue, LAR is "
                 "still 0.560 and 0.891 against a chance level of 0.250."},
        {"sec": "§ 5.7 · Localization", "title": "Failure localizes to Bengali",
         "body": "With random distractors, switching to English lifts every arm: Laya-ml +0.246, "
                 "Lod-lille +0.380, Jev-1.13 +0.230. Items right in English and wrong in Bengali: "
                 "37.4% and 43.3%; the reverse is 12.8% and 5.3%."},
    ]

    # the template names its click handlers with placeholders of their own;
    # keep them intact so clean() can turn them into data-act hooks
    for name in ("heroBn", "heroEn", "mxLar", "mxAcc", "copyBib"):
        d[name] = "{{ %s }}" % name

    d["item6"] = [
        {"l": "A", "text": "একগর্ভা; এক সন্তানের জননী; যে নারী একবার মাত্র গর্ভ ধারণ করে",
         "role": "distractor", "a": "0.00", "b": "0.02", "bg": "transparent", "wa": 400, "wb": 400},
        {"l": "B", "text": "ওজন (physical weight)", "role": "literal", "a": "0.99", "b": "0.15",
         "bg": "var(--color-accent-100)", "wa": 600, "wb": 400},
        {"l": "C", "text": "ক্ষমতা, গুরুত্ব, মর্যাদা", "role": "gold", "a": "0.00", "b": "0.82",
         "bg": "transparent", "wa": 400, "wb": 600},
        {"l": "D", "text": "হালকাভাবে পড়া", "role": "distractor", "a": "0.01", "b": "0.01",
         "bg": "transparent", "wa": 400, "wb": 400},
    ]
    return d


def fam_slots(family):
    kinds = ["gold"] + FAM[family]["s"]
    out = []
    for i, k in enumerate([2, 0, 3, 1]):
        kind = kinds[k]
        out.append({
            "letter": "ABCD"[i], "text": SLOT[kind]["t"], "tag": SLOT[kind]["tag"],
            "bd": ("var(--color-accent-800)" if kind == "lit"
                   else "var(--color-accent-400)" if kind == "gold" else "var(--color-divider)"),
            "bg": "var(--color-accent-100)" if kind == "lit" else "transparent",
            "tagc": "var(--color-accent-800)" if kind == "lit" else "var(--color-neutral-700)",
        })
    return out


PERMS = []
_perm = lambda a, r: PERMS.append(r) if not a else [ _perm(a[1:], r + [a[0]]) ]  # noqa: E731


def _gen_perms(a, r):
    if not a:
        PERMS.append(list(r))
        return
    for i in range(len(a)):
        _gen_perms(a[:i] + a[i + 1:], r + [a[i]])


_gen_perms([0, 1, 2, 3], [])
ORDER = [0, 9, 14, 23, 5, 18, 3, 12, 20, 7, 16, 1, 10, 21, 6, 15, 2, 19, 11, 22, 4, 13, 8, 17]


def perm_chips(i):
    perm = PERMS[ORDER[i % 24]]
    names = ["Gold figurative", "Literal gloss", "Distractor 1", "Distractor 2"]
    laya_pick = perm[1]
    out = []
    for g, text in enumerate(names):
        picks = []
        if laya_pick == g:
            picks.append(MODELS[0])
        if g == 1:
            picks.append(MODELS[1])
        if g == 0:
            picks.append(MODELS[2])
        out.append({
            "text": text, "y": f"{perm.index(g) * 52}px",
            "bd": ("var(--color-accent-800)" if g == 1
                   else "var(--color-accent-400)" if g == 0 else "var(--color-divider)"),
            "picks": [{"mk": p["mk"], "color": p["color"]} for p in picks],
        })
    return out


# ── mini template engine ─────────────────────────────────────────────────────

FOR_TAG = re.compile(r'<sc-for\b[^>]*>')
PH = re.compile(r"\{\{\s*([\w.]+)\s*\}\}")


def expand(html, data):
    """Expand <sc-for> loops and {{ }} placeholders into static markup.

    Loops are expanded outermost-first and each item's body is rendered
    recursively with that item in scope, so a nested loop sees its parent's
    fields (g.bars, p.picks, ...). A flat regex pass cannot do this: a
    non-greedy finditer never reports a match nested inside an earlier one.
    """
    return render(html, [], data)


def render(html, scopes, data):
    while True:
        m = FOR_TAG.search(html)
        if not m:
            break
        start, open_end = m.start(), m.end()
        header = html[start:open_end]
        key = re.search(r'list="\{\{\s*([\w.]+)\s*\}\}"', header)
        var = re.search(r'as="(\w+)"', header)
        if not key or not var:
            raise SystemExit(f"malformed sc-for: {header[:80]}")
        close, body = match_for(html, open_end)
        out = []
        for item in resolve(key.group(1), scopes, data):
            scope = item if isinstance(item, dict) else {"value": item}
            out.append(render(body, scopes + [(var.group(1), scope)], data))
        html = html[:start] + "".join(out) + html[close:]
    return PH.sub(lambda mm: str(field(mm.group(1), scopes, data)), html)


def match_for(html, pos):
    """Return (index past the matching </sc-for>, body) for a loop opened before pos."""
    depth, i = 1, pos
    while True:
        nxt_open = html.find("<sc-for", i)
        nxt_close = html.find("</sc-for>", i)
        if nxt_close == -1:
            raise SystemExit("unterminated sc-for")
        if nxt_open != -1 and nxt_open < nxt_close:
            depth += 1
            i = nxt_open + 1
            continue
        depth -= 1
        if depth == 0:
            return nxt_close + len("</sc-for>"), html[pos:nxt_close]
        i = nxt_close + 1


def resolve(name, scopes, data):
    head, _, rest = name.partition(".")
    for var, scope in reversed(scopes):
        if var == head:
            return scope[rest] if rest else list(scope.values())
    return data[name]


def field(name, scopes, data):
    head, _, rest = name.partition(".")
    for var, scope in reversed(scopes):
        if var == head:
            return scope.get(rest, "")
    val = data.get(name)
    return val if val is not None else ""


# ── charts ───────────────────────────────────────────────────────────────────

def svg_for(key):
    if key == "scatter":
        return CH.scatter()
    if key == "ladder":
        labels = ["random", "surface", "tag", "+ literal", "hard"]
        ci = [[[.357, .377], [.328, .347], [.324, .343], [.144, .159], [.137, .151]],
              [[.453, .516], [.380, .444], [.414, .478], [.051, .084], [.048, .080]]]
        return CH.grouped_bars(labels, [[0.367, 0.338, 0.333, 0.151, 0.144],
                                        [0.484, 0.412, 0.446, 0.066, 0.063]],
                               ci=ci, ymax=0.6, band=(2.5, 4.5))
    if key == "cues":
        labels = ["idiom not in gloss", "idiom in gloss", "no Latin cue", "Latin cue", "both cues absent"]
        return CH.grouped_bars(labels, [[0.616, 0.767, 0.581, 0.746, 0.560],
                                        [0.866, 0.986, 0.871, 0.909, 0.891]],
                               ymax=1.0, hatch_idx=None, band=(3.5, 4.5))
    if key == "xling":
        labels = ["Laya · BN", "Laya · EN", "Laya EN-ckpt · EN", "Laya EN-ckpt · BN",
                  "Lod · BN", "Lod · EN"]
        return CH.grouped_bars(labels, [[0.371, 0.617, 0.733, 0.283, 0.483, 0.864]],
                               ymax=1.0, hatch_idx={1, 2, 5}, xtickangle=-28)
    if key == "local":
        return CH.diverging(["Laya-ml", "Lod-lille"], [0.374, 0.433], [0.128, 0.053],
                            CH.C[:2])
    if key == "brier":
        return CH.hbars(["Laya-ml · BN", "Lod-lille · BN", "Jev-1.13 · BN", "Jev-1.13 · EN"],
                        [1.030, 1.391, 0.604, 0.110],
                        CH.C + [CH.C[2]], 1.6, "multiclass Brier score",
                        pattern_idx={3}, vline=0.75, vlabel="uniform 0.750")
    if key == "ece":
        return CH.lines(["random distractors", "+ literal (D-LIT)"],
                        [[0.071, 0.385], [0.073, 0.679], [0.005, 0.014]],
                        0, 0.75, 0.15, "ECE")
    if key == "ablate":
        return CH.lines(["full Bengali gloss", "truncated to 6 words", "word-scrambled",
                         "English gloss", "semantics removed"],
                        [[0.365, 0.361, 0.357, 0.347, 0.256], [0.492, 0.469, 0.479, 0.398, 0.233]],
                        0.15, 0.55, 0.1, "accuracy", show_labels=False)
    raise KeyError(key)


# ── assembly ─────────────────────────────────────────────────────────────────

RAW_TAGS = {"sc-raw-table": "table", "sc-raw-thead": "thead", "sc-raw-tbody": "tbody",
            "sc-raw-tr": "tr", "sc-raw-td": "td", "sc-raw-th": "th", "sc-raw-caption": "caption"}
ACTIONS = {"heroBn": "hero:bn", "heroEn": "hero:en", "mxLar": "matrix:lar", "mxAcc": "matrix:acc",
           "fm.pick": "family", "copyBib": "copy-bib"}


def clean(html):
    for a, b in RAW_TAGS.items():
        html = re.sub(rf"<{a}\b", f"<{b}", html).replace(f"</{a}>", f"</{b}>")
    html = re.sub(r'hint-placeholder-count="\d+"', "", html)
    html = re.sub(r'\sstyle-hover="[^"]*"', "", html)

    def act(m):
        name = m.group(1)
        if name in ACTIONS:
            return f'data-act="{ACTIONS[name]}"'
        raise SystemExit(f"unmapped interaction: {name}")

    html = re.sub(r'sc-camel-on-click="\{\{\s*([\w.]+)\s*\}\}"', act, html)

    # charts
    def plot(m):
        attrs, key = m.group(1), m.group(2)
        return f'<div class="plot"{attrs} data-chart="{key}">{svg_for(key)}</div>'

    html = re.sub(r'<div([^>]*?)data-plot="(\w+)"([^>]*)></div>', plot, html)
    return html


def mark_grow(html):
    """Give animated width/height elements a target the reveal can grow to."""
    def fix(m):
        tag, style, rest = m.group(1), m.group(2), m.group(3)
        if "data-grow" in tag:
            return m.group(0)
        for prop, attr in (("width", "data-w"), ("height", "data-h")):
            mm = re.search(rf'(?<![-\w]){prop}:calc\(([\d.]+)% - \d+px\)', style)
            if not mm:
                mm = re.search(rf'(?<![-\w]){prop}:([\d.]+)%', style)
            if mm:
                style = style.replace(f"{prop}:{mm.group(0).split(':', 1)[1]}",
                                      f"{prop}:var(--{prop[0]})")
                return f'<{tag} data-grow {attr}="{mm.group(1)}%" style="{style}"{rest}>'
        return m.group(0)

    return re.sub(r'<(\w+)([^>]*?)style="([^"]*)"([^>]*?)>', fix, html)


def head():
    def meta(*pairs):
        return "".join(f'  <meta {pairs[i]}="{pairs[i+1]}" {pairs[i+2]}="{pairs[i+3]}">\n'
                       for i in range(0, len(pairs), 4))

    ld = {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "headline": FULL_TITLE,
        "alternativeHeadline": "Literal Lock-In",
        "name": FULL_TITLE,
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
        "citation": ["Adib Sakhawat and Syed Rifat Raiyan. Literal Lock-In: How Test Language "
                     "Shifts Literal Attraction in Typed Decision Models on Bengali Idioms. "
                     "arXiv:2610.22526 [cs.CL], 2026."],
        "author": [{"@type": "Person", "name": "Adib Sakhawat",
                    "affiliation": {"@type": "CollegeOrUniversity", "name": "Islamic University of Technology"}},
                   {"@type": "Person", "name": "Syed Rifat Raiyan",
                    "affiliation": {"@type": "CollegeOrUniversity", "name": "Islamic University of Technology"}}],
        "publisher": {"@type": "Organization", "name": "arXiv", "sameAs": "https://arxiv.org"},
        "about": [{"@type": "Thing", "name": "Typed decision models"},
                  {"@type": "Thing", "name": "Bengali idioms"},
                  {"@type": "Thing", "name": "Literal attraction rate"},
                  {"@type": "Thing", "name": "Calibration of language models"}],
    }
    import json as _json
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{TITLE}</title>
{meta(
    "name", "description", "content", DESCRIPTION,
    "name", "keywords", "content", KEYWORDS,
    "name", "author", "content", "Adib Sakhawat, Syed Rifat Raiyan",
    "name", "robots", "content", "index, follow, max-image-preview:large, max-snippet:-1",
    "name", "twitter:card", "content", "summary_large_image",
    "name", "twitter:title", "content", TITLE,
    "name", "twitter:description", "content", DESCRIPTION,
    "name", "twitter:image", "content", CANONICAL + "og.png",
    "property", "og:type", "content", "article",
    "property", "og:site_name", "content", "Literal Lock-In",
    "property", "og:title", "content", TITLE,
    "property", "og:description", "content", DESCRIPTION,
    "property", "og:url", "content", CANONICAL,
    "property", "og:image", "content", CANONICAL + "og.png",
    "property", "og:image:width", "content", "1200",
    "property", "og:image:height", "content", "630",
    "property", "og:image:alt", "content", "Literal Lock-In on Bengali idioms",
    "property", "og:locale", "content", "en_US",
    "property", "article:published_time", "content", "2026-10-15T00:00:00Z",
    "property", "article:section", "content", "Computation and Language",
)}  <link rel="canonical" href="{CANONICAL}">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="og.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Noto+Serif+Bengali:wght@400;600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,500;0,8..60,600;1,8..60,400&display=swap">
  <script type="application/ld+json">
{_json.dumps(ld, ensure_ascii=False, indent=2)}
  </script>
"""


def main():
    data = build_data()
    body = (SRC / "template.html").read_text(encoding="utf-8")
    body = expand(body, data)
    body = clean(body)
    body = mark_grow(body)
    for leftover in ("<sc-for", "{{"):
        assert leftover not in body, f"unexpanded: {leftover}"

    css = (SRC / "site.css").read_text(encoding="utf-8")
    css += "\n" + CH.chart_css()
    css += """
/* reveal */
[data-reveal] .grow,[data-grow]{transition:transform .9s cubic-bezier(.2,.7,.2,1)}
.plot{margin-top:12px}
.plot .chart{opacity:0;transition:opacity .7s ease .2s}
.plot.on .chart{opacity:1}
@media (prefers-reduced-motion:reduce){*{animation-duration:.001ms!important;transition-duration:.001ms!important}}
"""

    js = (SRC / "app.js").read_text(encoding="utf-8")
    payload = {"bib": BIB, "fam": FAM, "slots": SLOT, "order": ORDER,
               "perms": PERMS, "larBn": [0.731, 0.918, 0.304], "larEn": [0.379, 0.241, 0.047],
               "accBn": [0.127, 0.044, 0.536], "accEn": [0.417, 0.684, 0.926]}
    import json as _json
    doc = f"""{head()}  <style>
{css}  </style>
</head>
<body>
<main>
{body}
</main>
<script type="application/json" id="site-data">{_json.dumps(payload, ensure_ascii=False)}</script>
<script>
{js}
</script>
</body>
</html>
"""
    OUT.write_text(doc, encoding="utf-8")
    print(f"wrote {OUT} ({len(doc) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()