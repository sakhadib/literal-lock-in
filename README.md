<h1 align="center">Literal Lock-In</h1>
<p align="center">
  <em>How test language shifts literal attraction in typed decision models on Bengali idioms</em><br>
  Adib Sakhawat* &nbsp;·&nbsp; Syed Rifat Raiyan* &nbsp;·&nbsp; Islamic University of Technology &nbsp;·&nbsp; *equal contribution
</p>
<p align="center">
  <a href="paper/acl_latex.pdf">Paper (PDF)</a> ·
  <a href="docs/index.html">Interactive site</a> ·
  <a href="#citation">BibTeX</a> ·
  <a href="https://anonymous.4open.science/r/FSS-CC4D">Anonymous review link</a>
</p>

Drop the idiom's own literal gloss into the option list, and three decision
models walk into it — a multilingual encoder scorer, a decoder scorer and a
closed commercial API. One shared item set, one option list, one switch: the
question in Bengali or its paired English entry. Every arm is **1.9× to 6.4×
more captured in Bengali**, and the arm that looks immune turns out to be immune
*in English*.

```text
অগ্নিবল  (agni-bal)   অগ্নি (fire) + বল (strength)   →   means  intense hunger
```

| Asked as | Laya-ml | Lod-lille | Jev-1.13 |
| --- | --- | --- | --- |
| Bengali idiom, both readings in the option list | **p = 1.00 on the literal** | **p = 0.97 on the literal** | **p = 0.36 on the literal** |
| Paired English entry | does not recover | recovers | recovers |

Across the 3,265 paired items, literal attraction falls from **0.731 / 0.918 /
0.304** in Bengali to **0.379 / 0.241 / 0.047** in English.

---

## Why this paper exists

Decision models — non-generative scorers that emit a probability over
caller-supplied options and no text at all — are increasingly deployed as
routers, classifiers and guardrails. Because they generate nothing, rationales
and chain-of-thought do not apply. There is no window into them except their
scores, so the usual explanation techniques have nothing to attach to.

This paper opens that window with one instrument: **the option list is the only
intervention surface.** A decision model returns a distribution over exactly the
options the caller supplies, so what you put in the list is a controlled
manipulation, not a prompt.

The corpus makes it possible because every row already ships two certified
readings. **Bangla Bagdhara** (Kaggle: `sakhadib/bangla-bagdhara`) annotates
10,361 Bengali idioms under a 19-field expert schema: a gold figurative meaning,
**and** an expert literal gloss. That gloss is a human-certified counterfactual
distractor already sitting in the data. No annotation was added for this study;
every intervention is assembled from fields that already exist.

## The instrument

**Task.** Given an idiom, pick its figurative meaning from `k = 4` candidates.
Chance is 0.250 throughout.

**Five distractor families — the independent variable.** Everything else (the
idiom, the instructions, `k`, the seed) is held fixed; only the option list moves.

| Family | Three distractors are… |
| --- | --- |
| `D-rand` | other idioms' glosses, drawn at random |
| `D-surf` | glosses sharing surface tokens with the gold |
| `D-sem` | glosses from idioms sharing a semantic tag |
| `D-lit` | one distractor replaced by the idiom's **own literal gloss** |
| `D-hard` | literal + surface + tag pressures at once |

**Literal Attraction Rate.** `LAR = (1/N) Σ 𝟙[argmax_o p_i(o) = ℓ_i]` over items
whose option list contains the literal gloss. LAR is **not** `1 − accuracy`: it
isolates the errors that are specifically a literal reading, and it has no
floor — a model that never reads literally scores 0 while still being wrong.

**Seven interventions, one variable each.** `E1` distractors · `E2` idiom surface
form · `E3` idiom form (unit integrity) · `E4` task language · `E5` calibration
and selective prediction (derived from E1) · `E6` option text · `E7` option
order. Paired McNemar throughout, with 95% percentile bootstrap intervals.

**Three arms.**

| Arm | Kind | Parameters | Items | Latency | Weights |
| --- | --- | --- | --- | --- | --- |
| `laya-ml` | bidirectional encoder, joint option scoring | 322M | 8,876 | 27.2 ms | open |
| `lod-lille-0.6b` | decoder, independent option scoring | 0.6B | 888 | 86.1 ms | open |
| `jev-1.13` | closed commercial model, decisions API | n/a | 8,761 | API | closed |

## What the instrument shows

1. **The stronger model leads until the literal gloss appears.** Lod-lille beats
   Laya-ml on every non-literal condition, by up to +0.133. Insert the idiom's
   own literal gloss and the ordering reverses: Lod-lille falls to 0.066 accuracy,
   half of Laya-ml's already-below-chance 0.136. A model can be picked as
   "better" on a conventional benchmark while being worse at what that benchmark
   proxies for.

2. **The error is not diffuse.** On the clearest items Laya-ml places p = 1.000
   on the literal gloss and 0.000 on the gold. Across the arms, the idiom's own
   literal gloss takes **66% to 96% of each arm's remaining Bengali errors**.

3. **Capture tracks the test language, not capability.** On the same 3,265
   paired items (paired McNemar p < 10⁻¹⁰⁰), the within-model language effect on
   LAR is +0.352, +0.677 and +0.256. Lod-lille is *more accurate than* Laya-ml and
   *more captured*; Jev-1.13 is *more accurate than both* and least captured. The
   commercial model's apparent resistance is a property of its test language. On
   the 5,485 corpus items with no English parenthetical cue, Bengali capture is
   still 0.581 and 0.871 for the open arms.

4. **Confidence is anti-diagnostic.** Both open models are *more* confident when
   captured than when correct. Laya-ml's most confident 5% under `D-lit` is 0.007
   accurate, against 0.151 at full coverage; Lod-lille answers **every** item in
   its most confident 35% incorrectly. Multiclass Brier under `D-lit` is 1.030 and
   1.391 — both worse than the 0.750 of a uniform four-way distribution. On both
   open arms, confidence-gated AURC is worse than gating at random. Jev-1.13 is
   well calibrated in English (ECE 0.014) and not on the same items in Bengali
   (ECE 0.135), where its edge over a random gate falls from 5.2× to 1.4×.

5. **Overconfidence survives the removal of all meaning.** The `O4` ablation
   replaces every option with a bare ordinal label — the four options stay
   distinguishable and carry nothing. Expected accuracy is 0.250; the
   best-calibrated model under real options, Jev-1.13, reports **mean confidence
   0.815 at 0.254 accuracy**.

6. **Order sensitivity is architecture-specific.** Every item runs under all 4! =
   24 orderings of a fixed option set. The marker-based scorer changes its chosen
   gloss on 83.7% of items, against 10.7% for the independent-option scorer and
   13.3% for the commercial one — a 7.8× spread in answer stability. Lod-lille is
   documented as order-independent by construction, and a single option's own
   score travels only 4.0×10⁻² at the median item.

7. **The idiom is not held as a stored unit.** Under word-shuffling, the open arms
   return the same option as on the intact idiom for 0.742 and 0.917 of items.
   Neither collapses. The manipulation that clearly helps both is embedding the
   idiom in its gold carrier sentence: +0.080 and +0.117.

8. **Failure localizes to Bengali.** With random distractors, switching the task
   to English lifts every arm (+0.246, +0.380, +0.230). Items answered correctly
   in English but wrongly in Bengali are 37.4% and 43.3%; the reverse is 12.8% and
   5.3%.

Two further controls rule out the obvious alternatives: on items with neither
verbatim overlap nor a Latin-script cue (n = 2,480 / 266), LAR is still 0.560 and
0.891; and expert-certified synonymous surface forms of the same idiom get only
0.657 and 0.677 answer agreement.

## Repository layout

| Path | What it is |
| --- | --- |
| `paper/` | LaTeX source (`acl_latex.tex`), ACL style, figures, bibliography |
| `analysis/` | Per-arm analysis scripts, audits, emitted tables (`tables/`), figures (`figures/`) |
| `LAYA_RUN/`, `LOD_RUN/`, `JEV_RUN/` | Raw per-item runs: `configs/`, `data/`, `results/<arm>/e{1..7}_*/` |
| `added/` | The model × language matrix run (all six cells from one seed) |
| `notebooks/` | Colab data-collection notebooks, one per arm |
| `tools/` | ACL `pubcheck` wrapper — see `tools/README.md` |
| `docs/index.html` | Self-contained interactive site (paper + figures, no network needed) |
| `perplexity/` | Background bibliography (54 entries), not part of the build |

## Reproducing

**Analysis** — pure Python over the released per-item outputs; no model calls, no
GPU. Needs `numpy`, `pandas`, `scipy`, `matplotlib`.

```sh
python3 analysis/analyze.py       # open arms  -> analysis/tables/{laya-ml,lod-lille-0.6b}/
python3 analysis/analyze_jev.py   # Jev arm    -> analysis/tables/jev-1.13/
python3 analysis/crossmodel.py    # 3-arm tests -> analysis/tables/_cross/
python3 analysis/tables_tex.py    # LaTeX tables -> analysis/tables/tables.tex
python3 analysis/figures.py       # paper figures
```

The `*_audit.py` scripts are the provenance checks the paper's claims rest on:
literal-gloss symmetry between the two language cells (`e4_gloss_audit.py`),
distractor construction (`item_construction_audit.py`), parenthetical and
lexical cues (`parenthetical_cue_audit.py`, `length_cue_audit.py`), and
order-sensitivity bookkeeping (`e7_order_audit.py`).

Bengali-script figures are rendered outside LaTeX, because `pdflatex` cannot
shape Bengali. `analysis/bangla_figures.py` drives Chromium through Playwright
(HarfBuzz) and emits true vector PDFs with embedded font subsets:

```sh
python3 -m pip install playwright && python3 -m playwright install chromium
python3 analysis/bangla_figures.py
```

**Data collection** is Colab-side and not needed to re-derive any number above.
`notebooks/*_FINAL_BOSS.ipynb` are the three collection runs (open encoder, open
decoder, closed API). All three pull the corpus with
`kagglehub.dataset_download("sakhadib/bangla-bagdhara")`. The closed arm
needs API credentials and is the only part that cannot be re-run offline.

**Paper build** — XeLaTeX, the TikZ stack and the Bengali font shipped in
`paper/`:

```sh
cd paper && latexmk -xelatex acl_latex.tex
tools/pubcheck.sh          # ACL format checks; tools/pubcheck.sh --refs adds the bibliography
```

`tools/pubcheck.sh` builds a second camera-ready copy, because `pubcheck` is
written for the final build and flags the line numbers that `[review]{acl}`
prints. `paper/acl_latex.pdf` is never touched.

## Data and provenance

`*/data/bagdhara_raw.jsonl` is the Bangla Bagdhara release as distributed
(10,359 records; the two missing rows are lost in the corpus's own export, not
in the loader). It is byte-identical across the run directories, and so is the
shared `full` split — the two open arms ran from identical per-item seeds over an
identically built table, verified before any paired test is reported.

The published count is 10,361 and the distributed file holds 10,359; of those,
8,876 carry every field the instrument requires. One methodological constraint is
enforced in code: Jev's ladder is English while the open arms' ladders are
Bengali, so literal-capture numbers are never put on one axis across all three.
Exactly one condition is identical across all three arms (the fully-Bengali
`D-rand` task), and it is the only place a three-way accuracy claim is made.

## Citation

```bibtex
@misc{sakhawat2026literal,
  title  = {Literal Lock-In: How Test Language Shifts Literal
            Attraction in Typed Decision Models on Bengali Idioms},
  author = {Sakhawat, Adib and Raiyan, Syed Rifat},
  year   = {2026},
  note   = {Equal contribution},
  url    = {https://github.com/sakhadib/literal-lock-in}
}
```

## License

Code, paper and figures: [CC BY-SA 4.0](LICENSE). The Bangla Bagdhara corpus is
redistributed as published and remains under its own terms.

## Notes

`paper/acl_latex.tex` is the **anonymous review build** (`\author{Anonymous
Submission}`, pointing at the anonymized artifact link) — it is kept that way on
purpose so the build can be submitted unmodified. This repository is the
de-anonymized artifact it points to. `docs/index.html` is a single self-contained
file: the paper PDF, the fonts and React are inlined, so it renders offline and
hosts unchanged on GitHub Pages.