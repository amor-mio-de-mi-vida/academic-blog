---
name: academic-blog
description: Write high-quality academic blog posts about AI / machine learning research as a single self-contained HTML page, Distill-style, with rigorous and beautiful figures (matplotlib data plots, hand-drawn SVG architecture/mechanism diagrams), KaTeX math, numbered figures/equations, citations, and clear explanatory prose. Use this skill whenever the user wants to write, draft, or polish a blog post, explainer, tutorial, paper walkthrough, paper reading notes for publication, technical essay or research write-up about an AI/ML/LLM topic (e.g. "写一篇博客解读这篇论文", "explain scaling laws in a blog post", "把我的实验结果写成技术博客", "用图解释 attention / RLHF / diffusion"), even if they don't say "academic" or "HTML" — and whenever figure quality, rigor, or readability of an ML explainer matters. Not for journal/conference manuscripts (use academic-paper for those).
---

# Academic blog (AI / ML)

Produce one HTML file that reads like a good Distill / research-lab blog post: a reader who did
not read the paper follows the argument, can check every piece of evidence, and leaves with a
correct mental model. Three qualities, in priority order:

1. **Rigorous**: every claim calibrated to its evidence, every number traceable to a source,
   every figure honest about what it shows.
2. **Clear**: question first, intuition before formalism, worked examples with real numbers,
   every symbol defined, figures that the text points into.
3. **Beautiful**: one consistent visual system for page, plots and diagrams — calm typography,
   colour-blind-safe palette, one accent colour for "the thing that matters".

Paths below use `SKILL_DIR` for this skill's directory (the folder containing this file).
Requirements: Python 3.8+, `uv` (for matplotlib), and Chrome/Chromium/Edge for previews. On
Windows write `python` where this file says `python3`.

## Bundled resources

| File | What it is | When to read |
|---|---|---|
| `references/writing.md` | How to structure and write the prose; rigor rules; Chinese typography | Before outlining |
| `references/data-figures.md` | Choosing chart forms for ML results, honesty rules, captions, code skeletons | Before the first data plot |
| `references/diagrams.md` | SVG diagram system: grid, classes, arrows, math in SVG, recipes | Before the first diagram |
| `references/components.md` | Copy-paste HTML snippets: figures, equations, citations, callouts, tables | While writing the source |
| `assets/template.html` | Page template with all CSS (also styles the diagrams) | Copy it to start |
| `assets/examples/attention.svg` | A finished reference diagram | Before the first diagram |
| `scripts/blogfig.py` | matplotlib house style + helpers (direct labels, bands, log axes, bars, heatmaps) | Import in plot scripts |
| `scripts/build_post.py` | Inlines figures, numbers figures/equations, resolves refs and citations, TOC, lint | After writing |
| `scripts/render.py` | Headless-Chrome previews: SVG → PNG, post → PDF/PNG | To look at your output |

## Workflow

### 0. Set up
Create a working folder named after the post slug (in the user's working directory unless they
say otherwise):
```
<slug>/
  <slug>.src.html      # copy of SKILL_DIR/assets/template.html — the source you edit
  outline.md           # step 2
  plots/               # one matplotlib script per data figure
  figs/                # generated .svg (+ .preview.png) and hand-written diagram .svg
  <slug>.html          # the deliverable, produced by build_post.py
```
Set `<html lang>` to `zh-CN` for Chinese posts (default in the template) or `en` (then also
rename the 参考文献 heading to References). Write in the language the user writes to you in
unless they ask otherwise. Replace every `{{...}}` placeholder in the header/footer; the build
reports each one left. Drop the author span if no author is known — never invent one.

### 1. Gather the facts first
Read the source material properly: the paper (PDF/arXiv), the user's notes, code or result
files. If you have web access, use it to read the actual paper and verify the related work you
plan to cite (download the PDF and extract text with
`uv run --with pypdf python -c "..."`; use `grep -a`, since extracted text often has odd bytes). Extract the specific numbers you will use together with where they come from
(e.g. "Table 3, row 2"). Facts you cannot verify are either left out or clearly labelled as
unverified. This step decides whether the post can be trusted, so don't rush it.
- **Rounded constants**: papers often print fitted constants rounded; derived results (optima,
  crossovers) can change noticeably. Recompute derived numbers from the constants, and use the
  arXiv TeX source or a replication for full precision when the paper's value doesn't reproduce.
- **Gated sources** (e.g. Meta model configs on Hugging Face): read a public mirror to verify,
  cite the official page, and say in the reference which copy you read.

### 2. Outline (write `outline.md`)
Read `references/writing.md`, then write:
- Title (a claim or a question), subtitle, TL;DR bullets (each a full claim).
- Target reader and what they already know.
- Sections: heading phrased as a claim + 1–2 lines on what it establishes + its worked example.
- **Figure plan** table: id · the one question it answers · form (data/diagram/table) ·
  data source (paper table X / computed / illustrative).
- A limitations section is part of every outline.

Aim for 3–7 figures for a typical post; every one must answer a question the text raises. If
the user is around and the topic is ambiguous, show them the outline; otherwise proceed.

### 3. Make the figures — and look at each one
- **Data figures**: read `references/data-figures.md`. One script per figure in `plots/`,
  importing `blogfig` (`sys.path.insert(0, "SKILL_DIR/scripts")`); call `bf.use(cjk=True)` when
  the figure has Chinese text. Run with
  `uv run --with matplotlib --with numpy python plots/<name>.py` (or any Python that has
  matplotlib + numpy). It writes `figs/<name>.svg` and `figs/<name>.preview.png`.
- **Diagrams**: read `references/diagrams.md` and look at `assets/examples/attention.svg`.
  Write `figs/<name>.svg` by hand using the template's `d-*` classes, then
  `python3 SKILL_DIR/scripts/render.py figs/<name>.svg` → `figs/<name>.preview.png`.
- **Fix every `blogfig OVERLAP` line** that `bf.save` prints: it detects labels that collide
  with other labels or that a line/marker passes through (the most common defect in testing).
  Move the label, shorten it, or draw the reference line elsewhere; re-run until none remain.
- **Open every preview PNG and inspect it.** Check clipping, legibility, that the takeaway is
  visible, that symbols match the equations — things the overlap check cannot see. Expect at
  least one round of fixes per figure.

### 4. Write the source
Fill `<slug>.src.html` using the snippets in `references/components.md`. It is fine to write the
body in a separate file and splice it into the template between `<article>` and `</article>`
with a small script, then replace the header/footer placeholders. Follow the ladder of
abstraction for each core idea: why → intuition → worked example with numbers → equation with
every symbol explained → implications. Reference each figure in the text and tell the reader
what to look at. Cite with `[@key]`, cross-reference with `@fig:` `@eq:` `@tab:` `@sec:`.

### 5. Build and lint
```bash
python3 SKILL_DIR/scripts/build_post.py <slug>/<slug>.src.html
```
Fix every ERROR (unresolved refs, missing provenance, uncited paper data, placeholders,
TODOs). Fix every WARNING too unless you have a stated reason: unreferenced figures/equations,
figures too small on phones, over-long equation rows, number-heavy TL;DR bullets, misplaced
sidenotes, ASCII quotes in Chinese, short captions, uncited references.

### 6. Review the rendered post
```bash
python3 SKILL_DIR/scripts/build_post.py <slug>/<slug>.src.html --offline   # review this build
python3 SKILL_DIR/scripts/render.py <slug>/<slug>.html           # -> <slug>.page-NN.png (desktop)
python3 SKILL_DIR/scripts/render.py <slug>/<slug>.html --phone   # -> <slug>.phone-NN.png (3 phone screens per image)
```
Open every desktop slice with Read, and at least the phone slices containing figures and
equations (phone slices show the 390 px page with a gray band on the right; that band is not
part of the page) (math
renders via KaTeX from a CDN, so this needs network). Look for: raw `\(` or red KaTeX errors,
display equations overflowing into the equation number, sidenotes floating next to the wrong
section, figures too small or too large relative to the text, wrapped table cells. Then go
through the self-review questions at the end of `references/writing.md` as the target reader,
including whether the TL;DR still matches what the body shows. Fix, rebuild, re-check.
(`--pdf` writes a print PDF if the user wants one.)

### 7. Deliver
Do the final build with `--offline`, which embeds KaTeX (scripts, CSS, fonts; ~0.6 MB, cached
after the first download) so the math renders without network — the file can then be emailed,
archived or opened anywhere:
```bash
python3 SKILL_DIR/scripts/build_post.py <slug>/<slug>.src.html --offline
```
Give the user the path to `<slug>.html` (single file; open it in any browser). Briefly list
what each figure shows and its data provenance, and flag anything you could not verify. The
`.src.html`, `plots/` and `figs/` stay alongside so the post can be edited and rebuilt.

## Non-negotiables (and why)

- **No invented numbers.** Every plotted or quoted number is from a cited source, from code
  you ran, or is visibly marked illustrative. Readers of research blogs quote numbers; a
  fabricated one spreads.
- **No invented references.** Only cite works you have verified exist and say what you claim.
- **Captions carry the takeaway** (bold first sentence), how to read the figure, and provenance,
  so a skimmer reading only figures still gets the argument right.
- **Every symbol defined, every acronym expanded** at first use — undefined notation is the
  main reason explainers fail their readers.
- **Limitations section** in every post — it is what makes the rest credible.
- **One visual system**: use `blogfig` for plots and the template's `d-*` classes for diagrams
  rather than ad-hoc styles, so the page looks designed rather than assembled.

## Output format notes
- The final HTML (built with `--offline`) is fully self-contained apart from web fonts, which
  load from Google Fonts and fall back to good system fonts (PingFang/Hiragino/Noto, Georgia,
  Helvetica) when offline.
- Light theme only: figures are designed for a white background, like a printed paper.
- Width: 680 px text column, 960 px wide figures, margin sidenotes on wide screens, responsive
  down to phone width.
