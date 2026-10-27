# Writing the explanatory text

The goal of an academic blog post is that a reader who did not read the paper can follow the
argument, check the evidence, and leave with a correct mental model. That needs two things that
usually pull against each other: being easy to follow and being exactly right. The rules below
are how to get both.

## Contents
1. Know the reader
2. Structure: question first, answer early
3. The ladder of abstraction (how to explain one idea)
4. Equations
5. Making figures and text work together
6. Rigor: claims, numbers, citations
7. Sentence-level style
8. Chinese-language posts
9. Final self-review questions

---

## 1. Know the reader

Default reader unless the user says otherwise: an ML-literate graduate student or engineer. They
know backprop, cross-entropy, transformers at the block-diagram level, and basic probability.
They do not know this specific paper, its notation, or the subfield's jargon.

Consequences:
- Do not re-explain what a neural network is. Do explain anything specific to this subfield
  (e.g. "KV cache", "μP", "GRPO") the first time it appears, in one sentence.
- Every acronym is expanded on first use.
- If the topic needs a prerequisite the reader may lack, give a short "background" section or a
  collapsible `<details class="deriv">` rather than derailing the main line.

## 2. Structure: question first, answer early

Readers decide in the first screen whether to keep reading. So:

1. **Title** states the finding or the question, not the paper name.
   "为什么大模型的损失随算力呈幂律下降" beats "Kaplan et al. 2020 解读".
2. **TL;DR box**: 3–5 bullets, each a complete claim someone could disagree with, readable in
   one breath: at most one key number per bullet. Details and intervals belong in the body.
3. **Motivation** (1–3 paragraphs): what problem, why it matters, what was confusing or
   unknown before. End with the question the post answers.
4. **Body sections**, each carrying one idea. Section headings are claims, not topics:
   "注意力是一次软性的字典查询" rather than "注意力机制". A reader skimming only headings should
   get the argument.
5. **What this does not show / limitations / open questions.** Required. This is where honesty
   lives: confounds, settings that were not tested, results that failed to replicate.
6. **Summary**: the takeaways again, now that the reader can understand them in full.
7. **References.**

Typical length: 2,000–5,000 words (or 4,000–10,000 Chinese characters). Shorter is better if
the argument is complete.

**Cover every part of the request in proportion.** Before outlining, list each thing the user
explicitly asked for (e.g. "why it becomes a bottleneck", "cover MQA/GQA", "a chart of X") and
make sure each gets a section or figure with real depth — not a paragraph squeezed between
others. For an engineering audience, a short runnable code snippet of the core mechanism is often
the clearest worked example.

**Concise beats exhaustive.** Cut any section the main argument does not need; move side topics
to sidenotes or `<details>`.

## 3. The ladder of abstraction

Explain each core idea by moving through these rungs, in this order:

1. **Why we need it**: the problem it solves, in one or two sentences.
2. **Intuition**: an analogy or a picture. ("Attention is a soft dictionary lookup: the query
   is compared against every key, and the values are blended by how well they matched.")
3. **Concrete worked example**: tiny, with real numbers the reader can check by hand
   (3 tokens, 2-dimensional vectors). This is the step most posts skip and the one that makes
   understanding stick.
4. **Formal statement**: the equation, with every symbol defined.
5. **What it implies**: consequences, edge cases, what changes if you vary a term.

Keep one **running example** through the whole post (the same toy sentence, the same model
size), so the reader is not re-loading context in every section.

Analogies must be checked: say where the analogy breaks ("unlike a real dictionary, every value
contributes a little"). An analogy that misleads is worse than none.

## 4. Equations

- Before an equation: say in words what it will express.
- After it: "read" it term by term, and define every symbol that is new. Use the pattern
  "其中 \( d_k \) 是键向量的维度" / "where \( d_k \) is the key dimension".
- Number an equation (give it an `id="eq-..."`) only if the text refers back to it.
- Use one notation throughout and keep it consistent with the figures (the diagram's
  \( W_Q \) is the equation's \( W_Q \)). If more than ~6 symbols, add a notation table.
- Long derivations go in `<details class="deriv">` so the main line stays readable and the rigor
  is still there for those who want it.
- Shapes matter in ML: state tensor shapes, e.g. \( Q \in \mathbb{R}^{T \times d_k} \).
- Inline math is `\( ... \)`; display math `\[ ... \]` or `$$ ... $$`. Single `$` does not render.

## 5. Making figures and text work together

- Reference every figure in the text **before** or at the point the reader needs it, and tell
  them what to look at: "在 @fig:scaling 中，注意三条曲线在约 10^21 FLOPs 处交叉。"
- The caption repeats the takeaway so a skimmer who reads only figures and captions still gets the
  argument (see data-figures.md for caption structure).
- Do not describe in prose what the figure already shows in full; use prose for the *why* and the
  figure for the *what*.
- A good rhythm: claim (text) → evidence (figure) → interpretation (text) → caveat (sidenote).

## 6. Rigor: claims, numbers, citations

This is what separates an academic blog from a content-marketing post.

**Calibrate every claim** to its evidence, and make the type visible to the reader:
- Proven / by definition: "由定义可知…", "it follows that…"
- Empirically observed, with a citation: "Kaplan 等人观察到… [@kaplan2020]"
- Your interpretation or speculation: "我们的理解是…", "one plausible explanation is…"
Never let speculation borrow the voice of an established result.

**Numbers**:
- Every number shown comes from (a) a cited paper, with the table/figure it came from;
  (b) code you actually ran; or (c) is explicitly marked illustrative. There is no fourth option.
- If you do not have the real numbers and cannot get them, draw an illustrative figure and say so
  (the build adds a visible "示意数据 / Illustrative" badge). Never produce plausible-looking fake
  benchmark numbers: readers will quote them.
- Keep the paper's precision; don't round 71.43 to "about 70%" in a table, but do round in prose
  when the exact value is not the point.
- Comparisons need the same setting: do not put numbers from different eval protocols on one
  axis without saying so.

**Citations**:
- Cite the original source, linked to arXiv `abs/` pages or the publisher's DOI.
- Verify that each reference exists and that it says what you attribute to it. If you have web
  access, check titles, authors, years and venues. If you cannot verify something, leave it out
  or say it is unverified; do not reconstruct references from memory and present them as checked.
- Cite specific locations for specific numbers: `[@kaplan2020, Fig. 1]`.

**Statistics with few runs** (typical: 3 seeds):
- Show every run (dots) next to the mean; with n = 3 the reader should see the spread.
- Use t-based intervals: the 95% CI of a mean of 3 runs is mean ± 4.30 × s.e. (t with 2 df),
  not ± 2 s.e. For a difference between two settings use Welch's t interval. Say "95% CI" and
  give it, rather than "x times the standard error".
- Keep distribution-free facts when they are the strongest evidence: "none of the 18 LoRA runs
  beat the worst full fine-tuning run" is more convincing than a mean difference.
- Fitting a trend (e.g. accuracy vs log rank) and reporting the slope with its CI is often
  clearer than many pairwise comparisons.

**Derived numbers and inferences**: when you compute something the source does not state
(e.g. inferring which layers LoRA was applied to from a parameter count), show the arithmetic
and call it an inference, and say whether it is unique.

**Comparing with the literature**: say a result is "consistent with" prior work only when it
matches in direction *and* rough size under comparable conditions; otherwise state the
difference plainly — that contrast is often the interesting finding.

**Distinguish** correlation from causation, "not significant" from "no effect", and the
paper's tested regime from extrapolations.

## 7. Sentence-level style

- One idea per sentence, one topic per paragraph. Lead a paragraph with its point.
- Section references: headings are long claims, so give each referenced heading a short label,
  `<h2 id="sec-limits" data-short="局限">…</h2>`, or write `[局限一节](@sec:limits)`.
- Concrete over abstract: "the 7B model" not "the larger configuration".
- Active voice; "we" for the reader-and-author journey ("我们先看一个只有三个词的例子").
- Cut hype: no "revolutionary", "game-changing", "颠覆性", "炸裂". Let results speak.
- Cut throat-clearing: no "In this blog post, we will…", "众所周知", "值得注意的是" as filler.
- Use sidenotes (`<aside class="sidenote">`) for tangents, caveats, historical asides — they keep
  the main line clean.
- Use callouts sparingly: `key` for the 1–3 central insights, `def` for definitions, `warn` for
  common misconceptions. If everything is highlighted, nothing is.

## 8. Chinese-language posts

- Space between Chinese and Latin letters/numbers: "使用 GPT-4 在 12 个任务上"
  (the convention most Chinese technical writing follows).
- Full-width punctuation in Chinese sentences （，。：；？！“”）; half-width inside code/math.
- Terms: on first use write 中文术语（English term）, e.g. 注意力（attention）, then use one form
  consistently. Keep established English terms where Chinese ML writing does (Transformer,
  token, embedding, batch, scaling law may stay English) — consistency matters more than purity.
- Figure/equation references: write "如@fig:x 所示" → renders "如图 3 所示".
- Type Chinese quotes as “ ” directly (the build warns about ASCII " next to Chinese text).
- Titles: if the h1 would break inside a word ("为什 / 么"), wrap the phrase in
  `<span class="nobr">…</span>` or insert a `<br>` at a natural pause.
- Prefer short sentences; long Chinese sentences with stacked 的 are hard to parse.

## 9. Final self-review questions

Read the built post top to bottom as the target reader and check:
1. Can I state the main claim after reading only title + TL;DR?
2. Do the section headings alone tell the argument?
3. Is every symbol defined before or right after first use? Every acronym expanded?
4. Does each core idea have a worked example with numbers?
5. Does every figure have a reason to exist (answers a question the text raises)?
6. For every number: where did it come from? Is that visible to the reader?
7. Is there anything I asserted more confidently than the evidence supports?
8. Is there a limitations section that a skeptical reviewer would find fair?
