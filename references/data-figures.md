# Data figures (plots of numbers)

A data figure is an argument made with evidence. It must be **true** (encodes the data
honestly), **legible** (readable at the size shown) and **pointed** (the reader sees the
takeaway in a few seconds). All data figures are made with matplotlib through
`scripts/blogfig.py`, saved as SVG and inlined into the post.

## Contents
1. Workflow
2. Choosing the chart form (AI-specific cases)
3. Honesty rules
4. Legibility and style
5. Captions
6. Code skeletons

---

## 1. Workflow

1. Write down the **one question** the figure answers ("Does the gain hold at larger scale?").
   If it answers two, make two figures or two panels.
2. Get the data and record where it came from (paper + table/figure, or your script). Put the
   numbers in the plot script as a clearly commented literal or load them from a CSV next to it.
3. Write `plots/<name>.py` using blogfig, run it, open `figs/<name>.preview.png` and **look at
   it**. Check: labels readable, nothing overlapping, the takeaway visible without the caption.
   Iterate until it is right; it rarely is on the first run.
4. Include it: `<figure id="fig-name" data-kind="data" data-source="paper|computed|illustrative">`.

Run plot scripts with `uv run --with matplotlib --with numpy python plots/name.py` from the post
folder (system `python3` usually lacks matplotlib). For numbers shared by several figures and the
prose (fitted constants, derived quantities), keep one `plots/common.py` and import it with
`sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))`; print the values the prose
quotes so you can copy them instead of retyping.

## 2. Choosing the chart form

| Question | Form | Notes |
|---|---|---|
| How does a metric evolve over training? | line plot, step/tokens on x | raw curve faint + EMA smoothed (`bf.smoothed`); state α. Several seeds → mean + band (`bf.band`). |
| How does X scale with compute / params / data? | **log–log** line + markers | `bf.log_axis` on both axes; draw the fitted power law as a thin line and write the fitted exponent; dashed where extrapolated beyond data. |
| Which method is better on a benchmark? | horizontal bars (`bf.hbars`) or dot plot with CIs | Zero baseline for bars. Few methods, many benchmarks → grouped dot plot / small multiples, not a giant grouped bar chart. |
| What does each component contribute? (ablation) | horizontal bars sorted by effect, or a delta plot vs. full model | Show the full model as reference line. |
| Trade-off between two metrics (accuracy vs. latency, cost vs. score) | scatter with direct labels, Pareto front line | Mark "better" direction with a small arrow/label. |
| Where does the model attend / what does it confuse? | heatmap (`bf.heatmap`) | Sequential colormap for magnitudes, diverging only for signed values centred at 0; always a labelled colorbar. |
| Distribution (of activations, lengths, rewards) | histogram / KDE / ECDF / violin | State bin width; log x if heavy-tailed. |
| Embedding geometry | 2-D projection scatter | Say which projection (PCA/t-SNE/UMAP) and that distances in t-SNE/UMAP are not meaningful globally. |
| Exact values matter more than shape | a table, not a chart | booktabs-style table in the template, best value in bold. |

Multi-panel figures: share axes when comparing (`sharey=True`), label panels (a)(b) with
`bf.panel_labels` and refer to them in the caption. Check that panel labels don't hit the top
tick label (leave headroom in `ylim`).

**Phones**: check every chart in the `--phone` render. Multi-panel figures: stack panels
vertically in a narrow figure (`bf.figure("narrow", nrows=2, aspect=1.1)`) unless the side-by-side
comparison is the point. Keep annotation text ≥ 10 pt; don't shrink blogfig's sizes to fit more
in — cut annotations instead.

**Each figure must add something no other figure shows.** If two figures share a y-quantity
(e.g. accuracy vs rank and accuracy vs parameter count, where params ∝ rank), merge them or drop
one. Prefer a figure that shows a *different* quantity (cost, the gap to a reference, per-seed
spread).

**Use the space for the data.** Don't stretch an axis to fit one far-away reference point
(e.g. full fine-tuning at 8B params next to LoRA at 1–200M): draw the reference as a labelled
horizontal line/band, or annotate it at the axis edge with an arrow.

## 3. Honesty rules

These are non-negotiable because a misleading figure is worse than no figure.

- **Provenance on every figure**: `data-source="paper"` (caption cites the paper and the
  table/figure), `"computed"` (you ran code; keep the script in `plots/`), or `"illustrative"`
  (synthetic data made to show a shape; the build adds a visible badge, and the caption says
  "示意 / schematic, not measured"). Never mix real and synthetic series in one plot without
  marking which is which.
- **No bars or lollipops on a log axis**: their length depends on an arbitrary baseline. Use
  dots (a dot plot) on log scales.
- **Claims match the evidence shown**: a general statement ("especially for small models")
  needs enough points to support it; with three examples, say "in these three models".
- **Bars start at zero.** If differences are small relative to the values, don't truncate the
  bars; use a dot plot or plot the difference instead.
- **Uncertainty**: if the source gives seeds/CIs/std, show them and name them in the caption
  ("shaded: ±1 s.d. over 3 seeds"). If the source reports a single run, say "single run" — the
  reader deserves to know the difference may be noise.
- **Log axes** are labelled as such (10^k ticks make it obvious). Never put a linear fit through
  data on a log plot or vice versa without saying so.
- **Smoothing is disclosed** and the raw curve stays visible.
- **Quantify comparisons, not just levels**: when the text says "A is 1.8 points below B", give
  the uncertainty of that difference (CI or s.d. over seeds) and say whether it exceeds seed noise.
- **Say what is missing**: if the data lacks a natural baseline (e.g. the untuned base model,
  the number of eval samples), state it — it limits what can be concluded.
- **Units are consistent** between text, tables and axes (GB vs GiB, tokens vs steps, % vs
  fraction). Pick one and say which in the axis label.
- **Same setting** on the same axis: same eval protocol, same number of shots, same data split.
  If not possible, separate panels and say why.
- **Extrapolation** is visually distinct (dashed, lighter) from fitted range.
- **No cherry-picking**: if the method loses on some benchmarks, show them.
- **Redraw, don't screenshot**: replot a paper's numbers from its tables instead of pasting its
  figure image. It is clearer, matches the post's style and avoids copyright issues. Cite it.

## 4. Legibility and style

blogfig sets most of this; know the reasons so you can make good exceptions.

- **Size for the page**: `bf.figure()` defaults to `"narrow"` (560 px). The build never scales
  a figure above its natural width, so it looks the same on desktop but shrinks only to ~70% on
  a 390 px phone (ticks stay ~9 px). Use `"column"` (680 px) only when the data needs the
  width, and `"wide"` (960 px) rarely — on phones it scrolls sideways. Height via `aspect`
  (0.5–0.7 typical; heatmaps square).
- **Direct labels over legends** (`bf.label_lines`): the eye doesn't have to jump back and forth.
  Use a legend only when there are many series or direct labels would collide.
- **No in-figure title**: the caption carries it. Axis labels state quantity and unit:
  "训练 token 数", "Test loss (nats/token)", "Compute (PF-days)".
- **Colour with meaning**: one accent (vermillion, `bf.ACCENT`) for the thing the figure is about
  (your method, the surprising curve); grays (`bf.GRAYS`) for baselines/context; Okabe–Ito
  (`bf.CATEGORICAL`) when several series are equally important. Colour-blind safe by default.
- **Never encode with colour alone**: add line styles, markers or direct labels so the figure
  survives grayscale and colour-blind readers.
- **Consistent mapping across the post**: if "Ours" is vermillion in Figure 1 it is vermillion
  everywhere. Define the mapping once in a small `plots/style_map.py` (or at the top of each
  script) and reuse it.
- **Annotate the point**: an arrow + short note (`bf.note`) at the crossover, the jump, the
  outlier the text discusses. `bf.note(..., textcoords="data")` places the text at a data
  position instead of an offset.
- **Split series** (solid fitted range + dotted extrapolation, or lines ending at different x):
  `bf.label_lines(ax, at_x=...)` labels all lines at the same x so labels don't land mid-plot.
- **Keep notes inside the axes**: a `bf.note` whose text extends past the left axis runs into
  the y-label; check the preview.
- **Reference lines vs labels**: draw dashed reference lines (20 tokens/param, full-FT level)
  first, then put value labels where no line passes — in the preview, every label must sit on
  clear background.
- **Labels along sloped lines** (iso-compute lines, power laws on log–log axes): use
  `bf.label_along(ax, x, y, text, line_xy=(xs, ys))`, which rotates the text to the line's
  on-screen angle.
- **Clipping**: set axis limits deliberately. A line that leaves the plot area, runs into the
  legend, or is cut at the top hides data; extend the limit, use a log axis, or annotate where it
  exits ("→ 64 GiB at 128k").
- **Consistent scales across related figures**: if two charts show the same quantity (context
  length, compute), use the same axis type and range unless there is a stated reason; readers
  compare them by position.
- **Collisions**: `bf.save` runs `bf.check_overlaps` and prints a `blogfig OVERLAP` line for
  every label that touches another label or that a line/marker crosses; fix them all. It cannot
  see collisions with filled areas or arrows, so also check the preview that no label touches a line (including fit lines and
  connectors drawn later), marker, error bar, panel edge or another label. Move it, shorten it, or use `bf.label_lines` / `bf.note` offsets.
- **Less ink**: no top/right spines, light y-grid only, no 3-D, no shadows, no gradient fills.
- **Math in labels** uses mathtext (`r"$d_k$"`), rendered in Computer Modern to match KaTeX.
  Powers too: `r"$10^{23}$"` — never Unicode superscripts like "10²³", which render broken.
- **Chinese labels**: call `bf.use(cjk=True)` in every plot script of a Chinese post. Without
  it, a label that mixes Chinese and math (`"验证损失 $\mathcal{L}$"`) shows empty boxes.

**Intervals**: compute every interval with blogfig's helpers so they are right for small n:
`bf.mean_ci(runs)` (t-based CI of a mean), `bf.welch_ci(a, b)` (CI of a difference),
`bf.slope_ci(x, y)` (CI of a fitted slope, e.g. gain per doubling of rank). Say "95% CI" in the
caption. No scipy needed.

## 5. Captions

Structure every caption in three parts:

1. **Bold takeaway sentence**: the claim the figure supports.
   `<b>测试损失随算力按幂律下降，且不同模型规模共享同一条包络线。</b>`
2. **How to read it**: what each axis/colour/band means, anything non-obvious (log scale,
   smoothing, what the dashed line is).
3. **Provenance**: "数据来自 [@kaplan2020, Fig. 1]" / "我们用 plots/scaling.py 计算" /
   "示意图，非实测数据".

## 6. Code skeletons

### Training curves, several seeds

```python
import sys; sys.path.insert(0, "SKILL_DIR/scripts")
import numpy as np, blogfig as bf
bf.use()
steps = ...            # shape [N]
runs = {"Baseline": ..., "Ours": ...}   # each: array [seeds, N]
fig, ax = bf.figure("column", aspect=0.55)
for name, y in runs.items():
    m, s = y.mean(0), y.std(0)
    bf.band(ax, steps, m, m - s, m + s, color=bf.ACCENT if name == "Ours" else bf.GRAYS[1], label=name)
bf.log_axis(ax, "x")
ax.set_xlabel("Training steps"); ax.set_ylabel("Validation loss")
bf.label_lines(ax)
bf.save(fig, "figs/curves")
```

### Scaling law fit

```python
C = np.array([...]); L = np.array([...])            # from paper table, cite it
b, log_a = np.polyfit(np.log10(C), np.log10(L), 1)  # L = a * C^b
fig, ax = bf.figure("column", aspect=0.6)
ax.plot(C, L, "o", color=bf.BLUE, label="measured")
xs = np.logspace(np.log10(C.min()), np.log10(C.max()), 50)
ax.plot(xs, 10**log_a * xs**b, color=bf.INK3, lw=1)
xe = np.logspace(np.log10(C.max()), np.log10(C.max()) + 1, 20)
ax.plot(xe, 10**log_a * xe**b, color=bf.INK3, lw=1, ls="--")   # extrapolation
bf.log_axis(ax, "x"); bf.log_axis(ax, "y")
bf.note(ax, xs[25], 10**log_a * xs[25]**b, rf"$L \propto C^{{{b:.3f}}}$", xytext=(20, 25))
```

### Benchmark comparison

```python
fig, ax = bf.figure("column", aspect=0.45)
# values copied from the paper's Table 2 (cite it in the caption); never invent them
bf.hbars(ax, ["Baseline A", "Baseline B", "Ours"], values, err=stderr, highlight="Ours")
ax.set_xlabel("Accuracy (%), 5-shot")
```
