# Concept diagrams (architectures, pipelines, mechanisms)

Diagrams explain *how something works*; data figures show *what happened*. In AI posts the
typical diagrams are: model architectures, data/training pipelines, an algorithm's steps, a
tensor's journey with shapes, matrix structure (masks, attention patterns), and before/after
comparisons of two methods.

Diagrams are **inline SVG** using the CSS classes defined in the template (hand-written, or
emitted by a small Python script in `plots/` when the drawing is repetitive — grids of cells,
token rows — or needs exact geometry such as contours; the script writes the SVG text with the
same `d-*` classes), so
every diagram in every post shares one visual language. A complete, rendered reference is in
`assets/examples/attention.svg` — read it before drawing your first diagram.

## Contents
1. Design principles
2. Canvas and grid
3. The class vocabulary
4. Arrows
5. Math and text inside SVG
6. Recipes for common AI diagrams
7. Checking your diagram

---

## 1. Design principles

- **Draw the idea, not just the boxes.** Ask what the reader must *see* to get the mechanism,
  and make the geometry carry it. LoRA's point is a narrow bottleneck: draw A and B as a
  trapezoid / thin matrices whose widths are proportional to d and r, not two equal boxes. A
  KV cache grows: draw it growing step by step. Equal-sized labelled boxes are the fallback when
  shape carries no meaning, not the default.
- **One diagram, one mechanism.** If you need a legend with ten entries, split it.
- **Faithful to the math.** Every box corresponds to an operation or tensor in the text, and
  uses the same symbol as the equations (\( W_Q \) in the equation ↔ "W_Q" in the box). A
  diagram that contradicts the equation is a bug.
- **Show shapes** where they help: `[B, T, d]` in mono under a tensor. Shapes are how ML readers
  check their understanding.
- **Direction of flow** is consistent: left→right for pipelines/data flow, bottom→top for layer
  stacks (as in the Transformer paper), top→bottom for algorithm steps.
- **One accent.** The vermillion `accent` class marks the single new or important component the
  post is about. Everything else is neutral (white/gray) or uses at most two muted category
  colours (blue/green) with a stated meaning.
- **Label what the reader must name.** Short labels inside boxes; explanatory phrases as small
  gray labels outside. Never a paragraph inside a diagram — that goes in the caption.
- **White space is structure.** Aligned edges and equal gaps read as order; jitter reads as
  noise.

## 2. Canvas and grid

- `viewBox="0 0 680 H"` for column width, `0 0 960 H` for `figure.wide`. **Do not** set
  `width`/`height` attributes; the build scales the SVG to the column and caps it at natural size.
- Work on an **8 px grid** (4 px for fine adjustments): box positions, sizes and gaps are
  multiples of 8. Standard box: height 40–48, corner radius 4. Gap between stages ≥ 40 so arrows
  are visible.
- Keep ≥ 16 px margin to the canvas edges; crop the viewBox to the content (shift its y origin
  instead of leaving empty bands).
- Minimum text size 12 px (mono/labels), 14 px for box labels, 16 px for math symbols.

## 3. The class vocabulary (defined in the template CSS)

| Class | Use |
|---|---|
| `d-box` | default node: white fill, dark stroke |
| `d-box soft` | secondary / given / frozen components (gray) |
| `d-box accent` | THE component the post is about (vermillion) |
| `d-box blue`, `green`, `purple`, `orange` | categories, e.g. encoder vs decoder; say so in caption |
| `d-group` | dashed container grouping several boxes (e.g. "× N layers") |
| `d-arrow` (+ `accent`, `muted`, `dashed`) | connectors; `dashed` = optional / gradient / feedback path |
| `d-head` (+ `accent`, `muted`) | arrowhead fill, used inside `<marker>` |
| `d-text`, `d-title` | 14 px labels, regular / semibold |
| `d-small`, `d-label` | 12 px secondary text, darker / lighter gray |
| `d-mono` | tensor shapes, code identifiers |
| `d-math`, `d-mathrm` | italic math symbols / upright math words (KaTeX fonts) |
| `d-accent-text` | text in the accent colour |
| `d-cell` | matrix cells (white separators); set `fill` per cell |

Use these classes rather than ad-hoc colours so all diagrams match the plots and the page. If you
truly need another colour, take it from the Okabe–Ito palette in the template tokens.

## 4. Arrows

Define markers once per SVG and attach them with the **attribute** `marker-end="url(#ah)"`
(not via CSS — the build rewrites ids to avoid collisions and only sees attributes):

```svg
<defs>
  <marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,1 L9,5 L0,9 z" class="d-head"/>
  </marker>
</defs>
<path class="d-arrow" d="M72 140 H110" marker-end="url(#ah)"/>
```

- Route with orthogonal segments (`H`/`V` commands) and turn at grid points; avoid diagonal
  spaghetti. A shared trunk that fans out (like X → W_Q, W_K, W_V in the example) reads cleaner
  than three separate arrows.
- End arrows 2 px before the target edge so the head touches but does not overlap the stroke.
- Label an arrow with what flows along it (a symbol or a shape), placed above horizontal segments.

## 5. Math and text inside SVG

KaTeX does not run inside SVG, so write math as styled text:
- Italic symbols: `<text class="d-math">x</text>`.
- Subscripts/superscripts with `dy` offsets (works in every browser; `baseline-shift` does not)
  and the `d-sub` class: `W<tspan class="d-sub" dy="5">Q</tspan>`,
  `K<tspan class="d-sub" dy="-7">⊤</tspan><tspan dy="7">…` (reset the offset in the next tspan).
- **Digits and upright symbols** (W₀, the 2 in x², "log"): add `d-up`, e.g.
  `W<tspan class="d-sub d-up" dy="5">0</tspan>`. KaTeX_Math has old-style digits, so a "0" in
  `d-math` looks like a small "o".
- CSS classes override SVG presentation attributes: `font-size="11"` on a tspan inside `d-math`
  is ignored. Use the classes above or an inline `style="font-size:11px"`.
- Avoid combining accents (L̂, x̃) in SVG text; the sans fonts render them badly. Write the hatted
  symbol in the caption's KaTeX instead, or use a short word label.
- Upright operators/words (softmax, log, √) with `d-mathrm`.
- Never write ASCII math like `d_h` or `H_kv` in a diagram: the prose shows \( d_h \) via KaTeX,
  and the figure must show the same symbol the same way.
- Centre text with `text-anchor="middle"` at the box centre x; vertical baseline ≈ box centre + 5
  for 14–16 px text.
- Text is real text (selectable, searchable) and uses the page fonts. Leave ≥ 8 px padding
  around labels inside boxes because readers' fonts can be slightly wider.
- **Width budget**: at 14 px a CJK character is ~14 px wide and a Latin character ~7.5 px; at
  12 px about 12 / 6.5 px. Size boxes from the longest label (chars × width + 16 px). SVG text
  does not wrap: break long labels into several `<text>` lines yourself.
- **Phone legibility trick**: the build caps an SVG at its natural (viewBox) width, so drawing
  a diagram on a *narrower* viewBox (e.g. 480 instead of 680) makes it look the same on desktop
  but ~1.4× larger on phones. Use it for diagrams with many small labels.
- **Wide diagrams on phones**: a 960 px diagram shrinks ~2.6× on a phone. The template lets
  wide diagrams scroll sideways below 640 px, but prefer column-width (680) diagrams, and keep
  labels ≥ 12 px so they survive scaling.

## 6. Recipes for common AI diagrams

**Pipeline / data flow** (tokenizer → model → sampler; RLHF stages): a single row of boxes on one
baseline, equal gaps, arrows labelled with what is passed. Stage numbers ①②③ in `d-label`
above boxes if the text walks through them.

**Layer stack** (Transformer block, residual stream): vertical, bottom→top. The residual stream
is a thick vertical line (`stroke-width: 3`, muted) with blocks reading from and writing back to
it via `⊕` circles. Wrap the repeated block in a `d-group` with "× N" label.

**Tensor-shape walkthrough**: boxes are operations, mono labels between them are shapes.
Highlight the dimension that changes in accent text.

**Matrix structure** (causal mask, attention pattern, KV cache): grid of `<rect class="d-cell">`
with fill from a 2–3 step scale (e.g. `#0072B2` / `#e8f1f8` / `#f2f2f0`). Label rows/cols with
tokens. For real attention values use a data heatmap instead (`bf.heatmap`).

**Before / after (method A vs B)**: two panels side by side at identical scale and layout,
titles "Standard" / "Proposed" in `d-title`, the difference in accent. Identical layout is what
makes the difference pop.

**Algorithm loop** (RL rollout → reward → update): boxes on a rounded rectangle path, arrows
clockwise, one dashed arrow for the gradient/feedback path.

**Geometry / intuition** (vectors, decision boundary, loss landscape cross-section): axes as thin
`d-arrow muted` lines, points as small circles (`r=4`), the key vector/angle in accent. If the
picture depends on real numbers, generate it with matplotlib instead so it is exact.

## 7. Checking your diagram

Render it and look:

```bash
python3 SKILL_DIR/scripts/render.py figs/arch.svg     # -> figs/arch.preview.png
```

Then read the PNG and check: nothing overlaps or is clipped; arrows connect to the right boxes;
labels are centred and readable; symbols match the equations; the accent marks the right thing;
no large empty bands (tighten the viewBox). Fix and re-render until clean — first drafts almost
always have an arrow or label a few pixels off.
