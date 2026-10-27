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
COLUMN = 680 / 96.0   # inches
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


def figure(width="column", aspect=0.62, nrows=1, ncols=1, **kw):
    """Create a figure sized for the page. width: 'column' | 'wide' | inches."""
    w = {"column": COLUMN, "wide": WIDE}.get(width, width)
    kw.setdefault("layout", "constrained")
    return plt.subplots(nrows, ncols, figsize=(w, w * aspect), **kw)


def panel_labels(axes, labels="abcdefgh", x=-0.02, y=1.02):
    """Bold (a), (b) ... labels at the top-left of each panel; refer to them in the caption."""
    for ax, lab in zip(np.ravel(axes), labels):
        ax.text(x, y, "(%s)" % lab, transform=ax.transAxes, fontsize=11, fontweight="bold",
                ha="right", va="bottom", color=INK)


def label_lines(ax, lines=None, texts=None, min_gap_px=15, dx_pt=6, **kw):
    """Direct-label lines at their right end (replaces a legend). Labels are nudged apart
    vertically so they never overlap; call AFTER setting axis limits/scales."""
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
        disp = ax.transData.transform((x[i], y[i]))
        pts.append([disp[1], disp[1], x[i], y[i], line.get_color(), t])
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
    return ax.annotate(text, (x, y), xytext=xytext, textcoords=textcoords, fontsize=10,
                       color=color, ha=kw.pop("ha", "left"), va=kw.pop("va", "center"),
                       arrowprops=dict(arrowstyle="-", color=color, linewidth=0.8,
                                       shrinkA=2, shrinkB=3), **kw)


def save(fig, path, preview=True):
    """Write <path>.svg for the post and <path>.preview.png for visual checking."""
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    # annotations outside the axes (direct labels, notes) are not part of the tight bbox by
    # default and get clipped; pass them explicitly
    extra = [t for ax in fig.axes for t in ax.texts]
    fig.savefig(path + ".svg", bbox_inches="tight", pad_inches=0.1, bbox_extra_artists=extra,
                metadata={"Date": None, "Creator": None})
    if preview:
        fig.savefig(path + ".preview.png", dpi=150, bbox_inches="tight", pad_inches=0.1,
                    bbox_extra_artists=extra)
    plt.close(fig)
    print("saved %s.svg%s" % (path, " and .preview.png" if preview else ""))
