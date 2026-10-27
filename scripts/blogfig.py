"""blogfig - matplotlib house style for academic-blog posts.

Import it from a plot script:

    import sys; sys.path.insert(0, "<skill>/scripts")
    import blogfig as bf
    bf.use()
    fig, ax = bf.figure("column", aspect=0.6)
    ...
    bf.save(fig, "figs/scaling")      # -> figs/scaling.svg (+ figs/scaling.preview.png)

Run with any Python that has matplotlib + numpy, e.g.
    uv run --with matplotlib --with numpy python plots/scaling.py

Sizing: a "column" figure is 680 CSS px wide, the post's text column, so 11 pt text in the
figure shows at ~14 px in the page, matching captions. "wide" is 960 px. Design the figure at
the size it will be shown; never rely on the browser scaling it.
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from cycler import cycler  # noqa: E402
from matplotlib import ticker  # noqa: E402

# ----------------------------------------------------------------------------- tokens
NARROW = 560 / 96.0   # inches; default for single-panel charts: readable on phones (~70% scale)
COLUMN = 680 / 96.0   # full text column; shrinks to ~55% on a 390 px phone
WIDE = 960 / 96.0

INK, INK2, INK3 = "#1a1a1a", "#4a4a4a", "#767676"
GRID = "#e6e6e3"
# Okabe-Ito, ordered so the first colours are most distinct on white. Colour-blind safe.
BLUE, VERMILLION, GREEN, PURPLE, ORANGE, SKY, BLACK = (
    "#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#000000")
CATEGORICAL = [BLUE, VERMILLION, GREEN, PURPLE, ORANGE, SKY, BLACK]
ACCENT = VERMILLION                         # "the new method / the thing to look at"
GRAYS = ["#4d4d4d", "#8c8c8c", "#b5b5b5"]   # baselines / context
SEQUENTIAL = "viridis"                      # magnitudes (attention, loss landscapes)
DIVERGING = "RdBu_r"                        # signed values with a meaningful zero
LINESTYLES = ["-", "--", ":", "-."]
MARKERS = ["o", "s", "^", "D", "v", "P"]

_LATIN = ["Helvetica Neue", "Helvetica", "Arial", "Inter", "Liberation Sans"]
_CJK = ["PingFang SC", "Hiragino Sans GB", "Noto Sans CJK SC", "Source Han Sans SC",
        "Microsoft YaHei", "Heiti SC", "WenQuanYi Micro Hei", "Arial Unicode MS"]


def _installed(names):
    have = {f.name for f in fm.fontManager.ttflist}
    return [n for n in names if n in have] or ["DejaVu Sans"]


def _warn_no_cjk():
    have = {f.name for f in fm.fontManager.ttflist}
    if not any(n in have for n in _CJK):
        print("blogfig WARNING: no CJK font found (tried %s); Chinese labels will show as boxes. "
              "Install e.g. Noto Sans CJK SC." % ", ".join(_CJK[:4]))


def use(cjk=False):
    """Apply the house style. Call once at the top of every plot script.

    cjk=True for figures with Chinese/Japanese text. It puts a CJK font first, because text
    outside $...$ in a label that also contains math is drawn with the FIRST font only (no
    per-glyph fallback there); PingFang / Noto CJK have clean Latin glyphs too."""
    import logging
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)  # weight-fallback noise
    if cjk:
        _warn_no_cjk()
    plt.rcParams.update({
        # A concrete family list (not the generic "sans-serif") is what enables matplotlib's
        # per-glyph fallback: Latin from Helvetica/Arial, CJK from PingFang/Hiragino/Noto.
        "font.family": _installed((_CJK + _LATIN) if cjk else (_LATIN + _CJK)) + ["DejaVu Sans"],
        "font.size": 11,
        "axes.labelsize": 11,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "text.color": INK,
        "axes.labelcolor": INK2,
        "axes.edgecolor": INK3,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "xtick.color": INK3,
        "ytick.color": INK3,
        "xtick.labelcolor": INK2,
        "ytick.labelcolor": INK2,
        "xtick.major.size": 3.5,
        "ytick.major.size": 3.5,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "xtick.minor.size": 2,
        "ytick.minor.size": 2,
        "axes.prop_cycle": cycler(color=CATEGORICAL),
        "lines.linewidth": 1.8,
        "lines.markersize": 5,
        "patch.linewidth": 0,
        "legend.frameon": False,
        "legend.handlelength": 1.6,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "figure.dpi": 100,
        "savefig.dpi": 200,
        "svg.fonttype": "path",        # glyphs as outlines: identical on every reader's machine
        "svg.hashsalt": "academic-blog",
        "mathtext.fontset": "cm",       # matches KaTeX in the body text
        "axes.unicode_minus": True,
        "image.cmap": SEQUENTIAL,
    })


def figure(width="narrow", aspect=0.62, nrows=1, ncols=1, **kw):
    """Create a figure sized for the page. width: 'narrow' (560 px, default) | 'column' (680) |
    'wide' (960) | inches. The build never upscales a figure past its natural width, so a
    narrow figure looks the same size on desktop but stays legible on phones."""
    w = {"narrow": NARROW, "column": COLUMN, "wide": WIDE}.get(width, width)
    kw.setdefault("layout", "constrained")
    return plt.subplots(nrows, ncols, figsize=(w, w * aspect), **kw)


def panel_labels(axes, labels="abcdefgh", x=-0.02, y=1.02):
    """Bold (a), (b) ... labels at the top-left of each panel; refer to them in the caption."""
    for ax, lab in zip(np.ravel(axes), labels):
        ax.text(x, y, "(%s)" % lab, transform=ax.transAxes, fontsize=11, fontweight="bold",
                ha="right", va="bottom", color=INK)


def label_lines(ax, lines=None, texts=None, min_gap_px=15, dx_pt=6, at_x=None, **kw):
    """Direct-label lines at their right end (replaces a legend). Labels are nudged apart
    vertically so they never overlap; call AFTER setting axis limits/scales.
    at_x: label every line at this x (interpolated) instead of its last visible point - use it
    when a series is split into solid + dotted segments or lines end at different x."""
    lines = lines or [l for l in ax.get_lines() if not l.get_label().startswith("_")]
    texts = texts or [l.get_label() for l in lines]
    fig = ax.figure
    fig.canvas.draw()
    pts = []
    for line, t in zip(lines, texts):
        x, y = np.asarray(line.get_xdata(), float), np.asarray(line.get_ydata(), float)
        ok = np.isfinite(x) & np.isfinite(y)
        x, y = x[ok], y[ok]
        (x0, x1), (y0, y1) = sorted(ax.get_xlim()), sorted(ax.get_ylim())
        inside = np.where((x >= x0) & (x <= x1) & (y >= y0) & (y <= y1))[0]
        if not len(inside):
            continue
        i = inside[-1]                                # last point actually visible
        lx, ly = x[i], y[i]
        if at_x is not None:
            order = np.argsort(x)
            lx, ly = at_x, float(np.interp(at_x, x[order], y[order]))
        disp = ax.transData.transform((lx, ly))
        pts.append([disp[1], disp[1], lx, ly, line.get_color(), t])
    pts.sort(key=lambda p: p[0])
    for k in range(1, len(pts)):                      # push up to keep min gap
        if pts[k][1] - pts[k - 1][1] < min_gap_px:
            pts[k][1] = pts[k - 1][1] + min_gap_px
    for p in pts:
        dy_pt = (p[1] - p[0]) * 72.0 / fig.dpi
        ax.annotate(p[5], (p[2], p[3]), xytext=(dx_pt, dy_pt), textcoords="offset points",
                    va="center", ha="left", color=p[4], fontsize=kw.get("fontsize", 10),
                    fontweight=kw.get("fontweight", "normal"), annotation_clip=False, clip_on=False)


def band(ax, x, mean, lo, hi, color=None, label=None, alpha=0.18, **kw):
    """Mean line with a shaded uncertainty band. ALWAYS say in the caption what the band is
    (e.g. '±1 s.d. over 5 seeds' or '95% bootstrap CI')."""
    line, = ax.plot(x, mean, color=color, label=label, **kw)
    ax.fill_between(x, lo, hi, color=line.get_color(), alpha=alpha, linewidth=0)
    return line


def ema(y, alpha=0.9):
    """Exponential moving average used for smoothing noisy curves. Disclose alpha in the caption."""
    y = np.asarray(y, float)
    out = np.empty_like(y)
    acc = y[0]
    for i, v in enumerate(y):
        acc = alpha * acc + (1 - alpha) * v
        out[i] = acc
    return out


def smoothed(ax, x, y, alpha=0.9, color=None, label=None, **kw):
    """Raw curve faint, EMA-smoothed curve on top, so smoothing never hides the noise."""
    raw, = ax.plot(x, y, color=color, alpha=0.22, linewidth=1, label="_raw")
    return ax.plot(x, ema(y, alpha), color=raw.get_color(), label=label, **kw)[0]


def log_axis(ax, which="x", base=10):
    """Log scale with 10^k major labels and unlabeled minor ticks."""
    axis = ax.xaxis if which == "x" else ax.yaxis
    (ax.set_xscale if which == "x" else ax.set_yscale)("log", base=base)
    axis.set_major_locator(ticker.LogLocator(base=base, numticks=12))
    axis.set_major_formatter(ticker.LogFormatterSciNotation(base=base))
    axis.set_minor_locator(ticker.LogLocator(base=base, subs=np.arange(2, 10) * 0.1, numticks=12))
    axis.set_minor_formatter(ticker.NullFormatter())


def human_format(ax, which="x", unit=""):
    """1.2K / 3.4M / 7B / 1.5T tick labels (parameters, tokens, FLOPs on linear axes)."""
    def f(v, _):
        for div, suf in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
            if abs(v) >= div:
                return ("%g" % round(v / div, 2)) + suf + unit
        return ("%g" % v) + unit
    (ax.xaxis if which == "x" else ax.yaxis).set_major_formatter(ticker.FuncFormatter(f))


def percent_axis(ax, which="y", decimals=0, xmax=100):
    (ax.xaxis if which == "x" else ax.yaxis).set_major_formatter(ticker.PercentFormatter(xmax, decimals))


def hbars(ax, labels, values, err=None, highlight=None, fmt="{:.1f}", color=None, sort=True):
    """Horizontal bar chart for benchmark / ablation comparisons. Zero baseline, value labels
    at bar ends, the highlighted entries in ACCENT and everything else gray."""
    labels, values = list(labels), np.asarray(values, float)
    err = None if err is None else np.asarray(err, float)
    idx = np.argsort(values) if sort else np.arange(len(values))[::-1]
    hl = set([highlight] if isinstance(highlight, str) else (highlight or []))
    cols = [(ACCENT if labels[i] in hl else (color or GRAYS[1])) for i in idx]
    y = np.arange(len(idx))
    ax.barh(y, values[idx], xerr=None if err is None else err[idx], color=cols, height=0.56,
            error_kw=dict(ecolor=INK3, elinewidth=1, capsize=2.5))
    ax.set_yticks(y, [labels[i] for i in idx])
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.set_xlim(0, None)
    ax.tick_params(axis="y", length=0)
    span = ax.get_xlim()[1]
    for yi, i in zip(y, idx):
        end = values[i] + (0 if err is None else err[i])
        ax.text(end + span * 0.01, yi, fmt.format(values[i]), va="center", ha="left", fontsize=9,
                color=ACCENT if labels[i] in hl else INK2,
                fontweight="bold" if labels[i] in hl else "normal")
    ax.set_xlim(0, span * 1.08)
    return ax


def heatmap(ax, M, xlabels=None, ylabels=None, cmap=SEQUENTIAL, vmin=None, vmax=None,
            center=None, cbar_label=None, annotate=False, fmt="{:.2f}"):
    """Matrix plot (attention maps, confusion matrices). Square cells, a labeled colorbar,
    diverging map centered at `center` when given."""
    from matplotlib.colors import TwoSlopeNorm
    M = np.asarray(M, float)
    norm = TwoSlopeNorm(vcenter=center, vmin=vmin, vmax=vmax) if center is not None else None
    im = ax.imshow(M, cmap=cmap if center is None else DIVERGING, vmin=None if norm else vmin,
                   vmax=None if norm else vmax, norm=norm, aspect="equal", interpolation="nearest")
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    if xlabels is not None:
        ax.set_xticks(range(len(xlabels)), xlabels, rotation=0 if max(map(len, xlabels)) < 4 else 45,
                      ha="center" if max(map(len, xlabels)) < 4 else "right")
    if ylabels is not None:
        ax.set_yticks(range(len(ylabels)), ylabels)
    ax.tick_params(length=0)
    if annotate:
        lo, hi = im.get_clim()
        for (i, j), v in np.ndenumerate(M):
            dark = (v - lo) / (hi - lo + 1e-12) < 0.55
            ax.text(j, i, fmt.format(v), ha="center", va="center", fontsize=8.5,
                    color="white" if dark else INK)
    cb = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.outline.set_visible(False)
    cb.ax.tick_params(length=0, labelsize=9)
    if cbar_label:
        cb.set_label(cbar_label)
    return im


def label_along(ax, x, y, text, line_xy, color=INK2, dy_pt=4, **kw):
    """Place `text` at data point (x, y), rotated to match the on-screen slope of the line given
    by line_xy=(xs, ys). Works on log axes. Call after limits and scales are final."""
    xs, ys = np.asarray(line_xy[0], float), np.asarray(line_xy[1], float)
    ax.figure.canvas.draw()
    p = ax.transData.transform(np.column_stack([xs, ys]))
    i = int(np.argmin(np.abs(p[:, 0] - ax.transData.transform((x, y))[0])))
    j = min(i + 1, len(p) - 1) if i + 1 < len(p) else i - 1
    ang = np.degrees(np.arctan2(p[j, 1] - p[i, 1], p[j, 0] - p[i, 0]))
    if ang > 90:
        ang -= 180
    elif ang < -90:
        ang += 180
    return ax.annotate(text, (x, y), xytext=(0, dy_pt), textcoords="offset points", rotation=ang,
                       rotation_mode="anchor", ha=kw.pop("ha", "center"), va="bottom",
                       fontsize=kw.pop("fontsize", 9), color=color, **kw)


def note(ax, x, y, text, xytext=(20, 20), color=INK2, textcoords="offset points", **kw):
    """Annotation with a thin arrow: use it to point at THE thing the caption talks about.
    xytext is an offset in points by default; pass textcoords="data" to give a data position."""
    return ax.annotate(text, (x, y), xytext=xytext, textcoords=textcoords,
                       fontsize=kw.pop("fontsize", 10),
                       color=color, ha=kw.pop("ha", "left"), va=kw.pop("va", "center"),
                       arrowprops=dict(arrowstyle="-", color=color, linewidth=0.8,
                                       shrinkA=2, shrinkB=3), **kw)


def _all_axes(fig):
    out = []
    def walk(ax):
        out.append(ax)
        for c in getattr(ax, "child_axes", []):
            walk(c)
    for ax in fig.axes:
        if ax not in out:
            walk(ax)
    return out


def _texts(fig, ticks=True):
    """Visible, non-empty texts that are actually drawn: annotations, axis labels, titles,
    legend entries, in-view tick labels (out-of-view ticks are skipped)."""
    from matplotlib.text import Text
    ts = list(fig.texts)
    for ax in _all_axes(fig):
        ts += list(ax.texts)
        ts += [a.label for a in (ax.xaxis, ax.yaxis)]
        ts += [getattr(ax, n, None) for n in ("title", "_left_title", "_right_title")]
        leg = ax.get_legend()
        if leg is not None:
            ts += list(leg.get_texts())
        if ticks:
            for axis in (ax.xaxis, ax.yaxis):
                ts += list(axis.get_majorticklabels()) + list(axis.get_minorticklabels())
    seen, out = set(), []
    for t in ts:
        if isinstance(t, Text) and id(t) not in seen and t.get_visible() and t.get_text().strip():
            seen.add(id(t))
            out.append(t)
    return out


def check_overlaps(fig, pad_px=1.0):
    """Find text that collides with other text or with plotted lines/markers.
    Returns a list of human-readable problems; save() prints them. Checks:
      - any two drawn texts (labels, annotations, legend entries, tick labels) that overlap
      - any annotation/label text that a data line or marker passes through
    Arrows, gridlines, spines and legend handles are ignored; rotated labels are tested
    against their rotated box."""
    from matplotlib.text import Text
    fig.canvas.draw()
    r = fig.canvas.get_renderer()

    def geom(t):
        bb = Text.get_window_extent(t, r)          # text only, not an annotation's arrow
        ang = np.radians(t.get_rotation() or 0.0)
        cx, cy = (bb.x0 + bb.x1) / 2, (bb.y0 + bb.y1) / 2
        c, s_ = abs(np.cos(ang)), abs(np.sin(ang))
        if abs(c - s_) < 0.2:                       # ~45°: fall back to a conservative box
            w, h = min(bb.width, bb.height) * 1.2, min(bb.width, bb.height) * 0.4
        else:                                       # solve W = w c + h s, H = w s + h c
            det = c * c - s_ * s_
            w = (bb.width * c - bb.height * s_) / det
            h = (bb.height * c - bb.width * s_) / det
        return bb, (cx, cy, ang, max(w, 1) / 2 - pad_px, max(h, 1) / 2 - pad_px)

    def inside(pts, g):
        cx, cy, ang, hw, hh = g
        d = pts - (cx, cy)
        u = d[:, 0] * np.cos(ang) + d[:, 1] * np.sin(ang)
        v = -d[:, 0] * np.sin(ang) + d[:, 1] * np.cos(ang)
        return (np.abs(u) < hw) & (np.abs(v) < hh)

    texts = [t for t in _texts(fig) if Text.get_window_extent(t, r).width > 0]
    gs = [(t,) + geom(t) for t in texts]
    name = lambda t: t.get_text().strip().replace("\n", " ")[:30]
    problems = []
    for i in range(len(gs)):
        for j in range(i + 1, len(gs)):
            a, b = gs[i], gs[j]
            if not a[1].overlaps(b[1]):
                continue
            # confirm with rotated boxes: sample b's corners/centre inside a, and vice versa
            def samples(g):
                cx, cy, ang, hw, hh = g
                loc = np.array([[0, 0], [hw, hh], [-hw, hh], [hw, -hh], [-hw, -hh], [hw, 0], [-hw, 0], [0, hh], [0, -hh]]) * 0.9
                rot = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]])
                return loc @ rot.T + (cx, cy)
            if inside(samples(b[2]), a[2]).any() or inside(samples(a[2]), b[2]).any():
                problems.append("text '%s' overlaps text '%s'" % (name(a[0]), name(b[0])))
    tick_ids = set()
    for ax in _all_axes(fig):
        for axis in (ax.xaxis, ax.yaxis):
            tick_ids.update(id(t) for t in axis.get_majorticklabels() + axis.get_minorticklabels())
    for ax in fig.axes:
        abox = ax.get_window_extent(r)
        for line in ax.get_lines():
            if not line.get_visible():
                continue
            ls_none = line.get_linestyle() in ("None", "none", "", " ") or line.get_linewidth() == 0
            if ls_none and line.get_marker() in (None, "None", "none", ""):
                continue
            xy = line.get_transform().transform(
                np.column_stack([line.get_xdata(orig=False), line.get_ydata(orig=False)]).astype(float))
            xy = xy[np.all(np.isfinite(xy), axis=1)]
            if len(xy) == 0:
                continue
            if ls_none:
                pts = xy
            else:
                pts = [xy[0]]
                for p0, p1 in zip(xy[:-1], xy[1:]):
                    n = int(max(1, np.hypot(*(p1 - p0)) // 2))
                    pts.extend(p0 + (p1 - p0) * k / n for k in range(1, n + 1))
                pts = np.array(pts)
            keep = ((pts[:, 0] >= abox.x0) & (pts[:, 0] <= abox.x1) &
                    (pts[:, 1] >= abox.y0) & (pts[:, 1] <= abox.y1))
            pts = pts[keep]
            if not len(pts):
                continue
            label = line.get_label()
            lname = ("line '%s'" % label) if not label.startswith("_") else "a line"
            for t, bb, g in gs:
                if id(t) in tick_ids or t.axes is not ax:
                    continue
                if inside(pts, g).any():
                    problems.append("%s passes through text '%s'" % (lname, name(t)))
    return sorted(set(problems))


def save(fig, path, preview=True, check=True):
    """Write <path>.svg for the post and <path>.preview.png for visual checking.
    With check=True (default) it also reports colliding labels; fix every one."""
    if check:
        for prob in check_overlaps(fig):
            print("blogfig OVERLAP in %s: %s" % (os.path.basename(path), prob))
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    # annotations outside the axes (direct labels, notes) are not part of the tight bbox by
    # default and get clipped; pass them explicitly
    extra = _texts(fig, ticks=False)
    fig.savefig(path + ".svg", bbox_inches="tight", pad_inches=0.1, bbox_extra_artists=extra,
                metadata={"Date": None, "Creator": None})
    if preview:
        fig.savefig(path + ".preview.png", dpi=150, bbox_inches="tight", pad_inches=0.1,
                    bbox_extra_artists=extra)
    plt.close(fig)
    print("saved %s.svg%s" % (path, " and .preview.png" if preview else ""))


# ----------------------------------------------------------------------------- statistics
# Small-sample helpers without scipy. Use them for every interval you plot or quote.
_T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306,
         9: 2.262, 10: 2.228, 12: 2.179, 15: 2.131, 20: 2.086, 25: 2.060, 30: 2.042, 40: 2.021,
         60: 2.000, 120: 1.980, 10 ** 9: 1.960}
_T95 = {1: 6.314, 2: 2.920, 3: 2.353, 4: 2.132, 5: 2.015, 6: 1.943, 7: 1.895, 8: 1.860,
        9: 1.833, 10: 1.812, 12: 1.782, 15: 1.753, 20: 1.725, 25: 1.708, 30: 1.697, 40: 1.684,
        60: 1.671, 120: 1.658, 10 ** 9: 1.645}


def t_quantile(df, conf=0.95):
    """Two-sided t critical value (conf 0.95 or 0.90); interpolates in 1/df for fractional df."""
    tab = {0.95: _T975, 0.90: _T95}[conf]
    ks = sorted(tab)
    df = max(float(df), 1.0)
    for lo, hi in zip(ks, ks[1:]):
        if lo <= df <= hi:
            w = (1 / lo - 1 / df) / (1 / lo - 1 / hi)
            return tab[lo] + w * (tab[hi] - tab[lo])
    return tab[ks[-1]]


def mean_ci(x, conf=0.95):
    """(mean, lo, hi): t-based CI of the mean. With 3 seeds this is mean ± 4.30 s.e."""
    x = np.asarray(x, float)
    m, se = x.mean(), x.std(ddof=1) / np.sqrt(len(x))
    h = t_quantile(len(x) - 1, conf) * se
    return m, m - h, m + h


def welch_ci(a, b, conf=0.95):
    """(diff, lo, hi, df): CI of mean(a) - mean(b) with Welch's unequal-variance t."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
    d, se = a.mean() - b.mean(), np.sqrt(va + vb)
    df = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
    h = t_quantile(df, conf) * se
    return d, d - h, d + h, df


def slope_ci(x, y, conf=0.95):
    """(slope, lo, hi): least-squares slope of y on x with a t-based CI (e.g. gain per
    doubling: slope_ci(np.log2(rank), acc))."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    b, a = np.polyfit(x, y, 1)
    resid = y - (a + b * x)
    se = np.sqrt(resid @ resid / (len(x) - 2) / ((x - x.mean()) @ (x - x.mean())))
    h = t_quantile(len(x) - 2, conf) * se
    return b, b - h, b + h
