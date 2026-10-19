"""Inline SVG charts for the static site.

The bundle drew these with Plotly at runtime. A static page has to carry the
marks in the markup instead, which is better anyway: the values are readable by
crawlers, the charts need no JS to exist, and hover text comes from <title>,
which every crawler and every screen reader already understands.

Geometry is a small fixed-scale plotter. viewBox scales it responsively.
"""
from html import escape

INK = "#1d1f20"
GRID = "rgba(29,31,32,0.09)"
C = ["var(--color-accent-800)", "var(--color-accent-500)", "var(--color-neutral-500)"]
SYM = ["circle", "square", "tri"]


def _sym(kind, x, y, r, fill, label):
    """A marker plus its <title>, so hover text needs no JS."""
    t = f"<title>{escape(label)}</title>"
    if kind == "circle":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}">{t}</circle>'
    if kind == "square":
        return (f'<rect x="{x - r:.1f}" y="{y - r:.1f}" width="{2 * r}" height="{2 * r}" '
                f'fill="{fill}">{t}</rect>')
    p = f"{x:.1f},{y - r - 1:.1f} {x - r - 1:.1f},{y + r:.1f} {x + r + 1:.1f},{y + r:.1f}"
    return f'<polygon points="{p}" fill="{fill}">{t}</polygon>'


class Plot:
    def __init__(self, w=560, h=320, ml=52, mr=16, mt=12, mb=54):
        self.w, self.h, self.ml, self.mr, self.mt, self.mb = w, h, ml, mr, mt, mb

    @property
    def pw(self):
        return self.w - self.ml - self.mr

    @property
    def ph(self):
        return self.h - self.mt - self.mb

    def sx(self, v, lo, hi):
        return self.ml + (v - lo) / (hi - lo) * self.pw

    def sy(self, v, lo, hi):
        return self.h - self.mb - (v - lo) / (hi - lo) * self.ph

    def frame(self, ylo, yhi, ystep, ylab, xlabels=None, xtickangle=0, yfmt="{:.2f}",
              xlabel=None, ticks=None):
        s = [f'<svg class="chart" viewBox="0 0 {self.w} {self.h}" role="img" '
             f'preserveAspectRatio="xMidYMid meet">']
        vals = ticks if ticks else [ylo + i * ystep
                                    for i in range(int(round((yhi - ylo) / ystep)) + 1)]
        for v in vals:
            y = self.sy(v, ylo, yhi)
            s.append(f'<line x1="{self.ml}" y1="{y:.1f}" x2="{self.w - self.mr}" y2="{y:.1f}" '
                     f'stroke="{GRID}" stroke-width="1"/>')
            txt = (("−" if v < 0 else "") + f"{abs(v):.0%}" if yfmt == "pct" else yfmt.format(v))
            s.append(f'<text x="{self.ml - 8}" y="{y + 4:.1f}" text-anchor="end" class="tick">'
                     f'{txt}</text>')
        s.append(f'<line x1="{self.ml}" y1="{self.h - self.mb}" x2="{self.w - self.mr}" '
                 f'y2="{self.h - self.mb}" stroke="{INK}" stroke-width="1"/>')
        if ylab:
            s.append(f'<text transform="translate(14,{self.mt + self.ph / 2:.1f}) rotate(-90)" '
                     f'text-anchor="middle" class="axis">{escape(ylab)}</text>')
        if xlabels:
            for i, lab in enumerate(xlabels):
                x = self.ml + (i + 0.5) * self.pw / len(xlabels)
                if xtickangle:
                    s.append(f'<text transform="translate({x:.1f},{self.h - self.mb + 14}) '
                             f'rotate({xtickangle})" text-anchor="end" class="tick">'
                             f'{escape(lab)}</text>')
                else:
                    s.append(f'<text x="{x:.1f}" y="{self.h - self.mb + 18}" text-anchor="middle" '
                             f'class="tick">{escape(lab)}</text>')
        return s

    def band(self, i0, i1, label=""):
        """Shaded region behind the bars, as the paper figures do for the literal families."""
        x0 = self.ml + i0 * self.pw / 5
        x1 = self.ml + i1 * self.pw / 5
        return (f'<rect x="{x0:.1f}" y="{self.mt}" width="{x1 - x0:.1f}" height="{self.ph}" '
                f'fill="rgba(214,235,255,0.55)"/>')

    def chance(self, value=0.25, lo=0.0, hi=1.0, label=None):
        y = self.sy(value, lo, hi)
        s = (f'<line x1="{self.ml}" y1="{y:.1f}" x2="{self.w - self.mr}" y2="{y:.1f}" '
             f'stroke="{INK}" stroke-width="1" stroke-dasharray="4 4"/>')
        if label:
            s += f'<text x="{self.ml + 4}" y="{y - 5:.1f}" class="tick">{escape(label)}</text>'
        return s

    def close(self):
        return "</svg>"


def _errbar(p, x, y, lo, hi, color=INK):
    """Bootstrap interval as a capped whisker."""
    return (f'<line x1="{x:.1f}" y1="{p.sy(lo, 0, 1):.1f}" x2="{x:.1f}" '
            f'y2="{p.sy(hi, 0, 1):.1f}" stroke="{color}" stroke-width="1"/>'
            f'<line x1="{x - 4:.1f}" y1="{p.sy(lo, 0, 1):.1f}" x2="{x + 4:.1f}" '
            f'y2="{p.sy(lo, 0, 1):.1f}" stroke="{color}" stroke-width="1"/>'
            f'<line x1="{x - 4:.1f}" y1="{p.sy(hi, 0, 1):.1f}" x2="{x + 4:.1f}" '
            f'y2="{p.sy(hi, 0, 1):.1f}" stroke="{color}" stroke-width="1"/>')


def scatter():
    """Model x language: accuracy against literal capture, one dot per cell."""
    names = ["Laya-ml", "Lod-lille", "Jev-1.13"]
    bnA, bnL = [0.127, 0.044, 0.536], [0.731, 0.918, 0.304]
    enA, enL = [0.417, 0.684, 0.926], [0.379, 0.241, 0.047]
    p = Plot(w=900, h=420, ml=58, mr=18, mt=14, mb=58)
    s = p.frame(0, 1, 0.25, "literal attraction rate")
    for i in range(5):
        v = i * 0.25
        x = p.sx(v, 0, 1)
        s.append(f'<line x1="{x:.1f}" y1="{p.mt}" x2="{x:.1f}" y2="{p.h - p.mb}" '
                 f'stroke="{GRID}" stroke-width="1"/>')
        s.append(f'<text x="{x:.1f}" y="{p.h - p.mb + 18}" text-anchor="middle" class="tick">'
                 f'{v:.2f}</text>')
    s.append(f'<text x="{p.ml + p.pw / 2:.1f}" y="{p.h - 8}" text-anchor="middle" '
             f'class="axis">accuracy (literal condition)</text>')
    s.append(p.chance(0.25, 0, 1, "chance"))
    for i, n in enumerate(names):
        x1, y1 = p.sx(bnA[i], 0, 1), p.sy(bnL[i], 0, 1)
        x2, y2 = p.sx(enA[i], 0, 1), p.sy(enL[i], 0, 1)
        s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{C[i]}" '
                 f'stroke-width="1.5" stroke-dasharray="2 4"/>')
        s.append(_sym(SYM[i], x1, y1, 8, C[i], f"{n} · Bengali · accuracy {bnA[i]:.3f} · LAR {bnL[i]:.3f}"))
        s.append(_sym(SYM[i], x2, y2, 8, "none", f"{n} · English · accuracy {enA[i]:.3f} · LAR {enL[i]:.3f}"))
        s.append(f'<text x="{x1 + 12:.1f}" y="{y1 - 10:.1f}" class="tick">{escape(n)}</text>')
    return "".join(s) + p.close()


def grouped_bars(labels, series, ci=None, ymax=1.0, ylab="accuracy", hatch_idx=None,
                 band=None, xtickangle=0):
    """Grouped vertical bars. series = list of value lists, one per model."""
    p = Plot()
    s = p.frame(0, ymax, ymax / 5 if ymax <= 1 else 0.1, ylab, labels, xtickangle=xtickangle)
    if band:
        s.insert(1, p.band(*band))
    s.append(p.chance(0.25, 0, ymax, "chance" if ymax >= 0.25 else None))
    n, m = len(labels), len(series)
    slot = p.pw / n
    bw = min(30, slot / (m + 1))
    for gi in range(n):
        cx = p.ml + (gi + 0.5) * slot
        for mi in range(m):
            v = series[mi][gi]
            x = cx + (mi - (m - 1) / 2) * (bw + 2) - bw / 2
            y = p.sy(v, 0, ymax)
            hatch = hatch_idx and gi in hatch_idx
            fill = "none" if hatch else C[mi]
            dash = ' stroke-dasharray="4 3"' if hatch else ""
            s.append(
                f'<rect class="grow" x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" '
                f'height="{p.sy(0, 0, ymax) - y:.1f}" fill="{fill}" stroke="{C[mi]}" '
                f'stroke-width="1.5" data-grow="{p.sy(0, 0, ymax) - y:.1f}"'
                f'{dash} style="--h:{p.sy(0, 0, ymax) - y:.1f}px">'
                f'<title>{escape(NAMES[mi])} · {escape(labels[gi])}: {v:.3f}</title></rect>')
            if ci:
                s.append(_errbar(p, x + bw / 2, y, ci[mi][gi][0], ci[mi][gi][1]))
    return "".join(s) + p.close()


NAMES = ["Laya-ml", "Lod-lille", "Jev-1.13"]


def lines(labels, series, ylo, yhi, ystep, ylab, show_labels=True):
    """Line + marker per model, x labels supplied as text above the marks."""
    p = Plot(h=300, ml=52, mb=40)
    s = p.frame(ylo, yhi, ystep, ylab)
    for i, lab in enumerate(labels):
        for mi, ys in enumerate(series):
            if i:
                x0, x1 = p.sx(i - 1, 0, len(labels) - 1), p.sx(i, 0, len(labels) - 1)
                y0, y1 = p.sy(ys[i - 1], ylo, yhi), p.sy(ys[i], ylo, yhi)
                s.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
                         f'stroke="{C[mi]}" stroke-width="2"/>')
            x, y = p.sx(i, 0, len(labels) - 1), p.sy(ys[i], ylo, yhi)
            s.append(_sym(SYM[mi], x, y, 6, C[mi],
                          f"{NAMES[mi]} · {labels[i].replace('<br>', ' ')}: {ys[i]:.3f}"))
            if show_labels:
                s.append(f'<text x="{x:.1f}" y="{y - 12:.1f}" text-anchor="middle" class="tick">'
                         f'{ys[i]:.3f}</text>')
    return "".join(s) + p.close()


def hbars(labels, values, colors, xmax, xlabel, pattern_idx=None, vline=None, vlabel=None):
    """Horizontal bars, used for the Brier comparison."""
    p = Plot(w=560, h=260, ml=112, mr=46, mt=10, mb=44)
    s = p.frame(0, xmax, xmax / 4, None, xlabel=xlabel)
    if vline:
        x = p.sx(vline, 0, xmax)
        s.append(f'<line x1="{x:.1f}" y1="{p.mt}" x2="{x:.1f}" y2="{p.h - p.mb}" stroke="{INK}" '
                 f'stroke-dasharray="4 4"/>')
        s.append(f'<text x="{x:.1f}" y="{p.mt - 1}" text-anchor="middle" class="tick">'
                 f'{escape(vlabel)}</text>')
    slot = p.ph / len(labels)
    bh = min(26, slot * 0.55)
    for i, (lab, v) in enumerate(zip(labels, values)):
        y = p.mt + (i + 0.5) * slot - bh / 2
        w = p.sx(v, 0, xmax) - p.ml
        hatch = pattern_idx and i in pattern_idx
        s.append(f'<rect class="grow" x="{p.ml}" y="{y:.1f}" width="{w:.1f}" height="{bh:.1f}" '
                 f'fill="{"none" if hatch else colors[i]}" stroke="{colors[i]}" stroke-width="1.5"'
                 f'{" stroke-dasharray=\'4 3\'" if hatch else ""} '
                 f'data-grow="{w:.1f}" style="--w:{w:.1f}px">'
                 f'<title>{escape(lab)}: {v:.3f}</title></rect>')
        s.append(f'<text x="{p.ml + w - 8:.1f}" y="{y + bh / 2 + 4:.1f}" text-anchor="end" '
                 f'class="tick" fill="#ffffff">{v:.3f}</text>')
        s.append(f'<text x="{p.ml - 8}" y="{y + bh / 2 + 4:.1f}" text-anchor="end" '
                 f'class="tick">{escape(lab)}</text>')
    return "".join(s) + p.close()


def diverging(labels, right, left, colors):
    """Share right-in-one-language-only vs the reverse, around a zero line."""
    p = Plot(w=560, h=240, ml=78, mr=18, mt=26, mb=46)
    s = p.frame(-0.2, 0.5, 0.1, None,
                ticks=[-0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5], yfmt="pct")
    x0 = p.sx(0, -0.2, 0.5)
    s.append(f'<line x1="{x0:.1f}" y1="{p.mt}" x2="{x0:.1f}" y2="{p.h - p.mb}" stroke="{INK}"/>')
    slot = p.ph / len(labels)
    bh = 22
    for i, (lab, r, l) in enumerate(zip(labels, right, left)):
        y = p.mt + i * slot + 4
        for val, color, hatch in ((r, colors[i], False), (-l, colors[i], True)):
            x = p.sx(min(val, 0), -0.2, 0.5)
            w = abs(p.sx(val, -0.2, 0.5) - x0)
            s.append(f'<rect class="grow" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" '
                     f'height="{bh:.1f}" fill="{"none" if hatch else color}" stroke="{color}" '
                     f'stroke-width="1.5"{" stroke-dasharray=\'4 3\'" if hatch else ""} '
                     f'data-grow="{w:.1f}" style="--w:{w:.1f}px">'
                     f'<title>{escape(lab)} · {abs(val):.1%} '
                     f'{"right in English only" if val > 0 else "right in Bengali only"}</title></rect>')
        s.append(f'<text x="{p.ml - 8}" y="{y + bh / 2 + 4:.1f}" text-anchor="end" class="tick">'
                 f'{escape(lab)}</text>')
    s.append(f'<text x="{p.sx(0.15, -0.2, 0.5):.1f}" y="{p.mt - 8}" text-anchor="middle" '
             f'class="tick">English only →</text>')
    s.append(f'<text x="{p.sx(-0.1, -0.2, 0.5):.1f}" y="{p.mt - 8}" text-anchor="middle" '
             f'class="tick">← Bengali only</text>')
    return "".join(s) + p.close()


def chart_css():
    return """
.chart{display:block;width:100%;height:auto;overflow:visible}
.chart .tick{font-family:var(--font-mono);font-size:10px;fill:var(--color-neutral-700)}
.chart .axis{font-family:var(--font-heading);font-size:12px;fill:var(--color-text)}
.chart .grow{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);
  transition:transform .9s cubic-bezier(.2,.7,.2,1)}
.chart .grow[style*="--w"]{transform-origin:left center;transform:scaleX(0)}
.chart.on .grow,.chart.grown .grow{transform:scaleY(1)}
.chart.on .grow[style*="--w"],.chart.grown .grow[style*="--w"]{transform:scaleX(1)}
@media (prefers-reduced-motion:reduce){.chart .grow{transition:none;transform:none}}
"""