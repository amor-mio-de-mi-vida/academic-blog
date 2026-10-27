# HTML components (copy-paste snippets for the post source)

Write the post in `<slug>.src.html`, a copy of `assets/template.html`. Everything below goes
inside `<article>`. `build_post.py` turns the source into the final self-contained `<slug>.html`.

## Section heading
```html
<h2 id="sec-mechanism" data-short="注意力机制">注意力是一次软性的字典查询</h2>
<!-- @sec:mechanism renders the data-short text; [这一节](@sec:mechanism) uses your own words.
     The same [text](@fig:x) form works for figures, tables and equations. -->
<h3>一个三词的例子</h3>                                <!-- id auto-assigned -->
```
Add `class="no-toc"` to keep a heading out of the table of contents (the TOC appears
automatically when there are ≥ 3 h2 sections).

## Data figure
```html
<figure id="fig-scaling" data-kind="data" data-source="paper">
  <div class="fig-body"><!-- @include figs/scaling.svg --></div>
  <figcaption><b>损失随算力按幂律下降。</b>横纵轴均为对数刻度；灰线为拟合的幂律，虚线部分为外推。数据来自 [@kaplan2020, Fig. 1]。</figcaption>
</figure>
```
- `data-source`: `paper` (caption must cite), `computed` (add `data-script="plots/x.py"`),
  `illustrative` (gets a visible 示意数据 badge).
- Add `class="wide"` to `<figure>` for 960 px figures.

## Diagram
```html
<figure id="fig-arch" data-kind="diagram">
  <div class="fig-body"><!-- @include figs/arch.svg --></div>
  <figcaption><b>一次注意力计算的完整数据流。</b>输入 \(X\) 经三个投影得到 \(Q, K, V\)；橙色的 softmax 把相似度变成每行和为 1 的权重。</figcaption>
</figure>
```

## Table
```html
<figure id="tab-results" class="table" data-source="paper">
  <figcaption><b>在相同训练预算下，新方法在 4 个基准中的 3 个上更好。</b>5-shot 准确率（%）；粗体为每列最佳。数据来自 [@paper2024, Table 2]。</figcaption>
  <div class="table-wrap"><table>
    <thead><tr><th>方法</th><th class="num">MMLU</th><th class="num">GSM8K</th></tr></thead>
    <tbody>
      <tr><td>Baseline</td><td class="num">…</td><td class="num"><strong>…</strong></td></tr>
      <tr class="ours"><td>Ours</td><td class="num"><strong>…</strong></td><td class="num">…</td></tr>
      <tr class="ref"><td class="nowrap">Full fine-tuning</td><td class="num">…</td><td class="num">…</td></tr>
    </tbody>
  </table></div>
</figure>
```
`tr.ours` highlights the proposed method, `tr.ref` a reference/baseline row; `td.nowrap` keeps
model names on one line. Caption goes above a table (convention), below a figure. Tables computed from data use
`data-source="computed"` (plus `data-script`), illustrative ones `"illustrative"`. Keep tables to
about 6 numeric columns in the 680 px column; split or transpose wider ones.

## Equations
```html
<div class="eq" id="eq-attn">\[ \mathrm{Attention}(Q,K,V)=\softmax\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V \]</div>
<p>其中 \( Q \in \R^{T\times d_k} \) 是查询矩阵，……（逐项解释）</p>
```
- Numbered only when it has an `id` (`eq-...`); reference as `@eq:attn`.
- Inline math: `\( ... \)`. Display: `\[ ... \]` or `$$ ... $$`. Never single `$`.
- Shared macros (`\R`, `\E`, `\softmax`) live in `window.POST_MACROS` at the bottom of the
  template; add the post's own notation there (e.g. `"\\Hkv": "H_{\\mathrm{kv}}"`).
- Long display equations overflow on narrow screens and collide with the equation number:
  split them with `\begin{aligned} ... \\ ... \end{aligned}` or `gathered`.

## Cross-references and citations
```html
如@fig:scaling 所示 … 由@eq:attn 可得 … 详见 @sec:limits。
这一现象最早由 Kaplan 等人报告 [@kaplan2020]，后被修正 [@hoffmann2022; @besiroglu2024]。
具体数值见 [@hoffmann2022, Table 3]。
```
Reference list (order does not matter; the build numbers by first citation):
```html
<ol class="references">
  <li data-key="kaplan2020">Kaplan, J., McCandlish, S., Henighan, T., et al. (2020). <a href="https://arxiv.org/abs/2001.08361">Scaling Laws for Neural Language Models</a>. <i>arXiv:2001.08361</i>.</li>
</ol>
```

## TL;DR, callouts, sidenotes
```html
<div class="tldr"><p class="tldr-title">TL;DR</p><ul><li>…</li></ul></div>

<div class="callout key"><p class="callout-title">核心结论</p><p>…</p></div>
<div class="callout def"><p class="callout-title">定义</p><p>…</p></div>
<div class="callout warn"><p class="callout-title">常见误解</p><p>…</p></div>

<aside class="sidenote">放在它所注释的段落<b>之前</b>：宽屏时浮在右侧页边，窄屏时内联显示。</aside>
<p>正文段落……</p>
```
The sidenote floats next to whatever follows it. Put it immediately BEFORE the paragraph it
annotates — never after a paragraph or before a heading, or it drifts next to the next section.
Check every sidenote's position in the rendered slices; the lint cannot see this.
```html
```

## Optional depth
```html
<details class="deriv"><summary>推导：为什么要除以 √d_k</summary>
  <p>……</p>
</details>
```

## Code
```html
<pre><code>scores = q @ k.transpose(-2, -1) / math.sqrt(d_k)</code></pre>
```
Escape `<`, `>` and `&` inside code. Keep snippets short (≤ 20 lines) and runnable in spirit.

## Notation table (when > ~6 symbols)
```html
<div class="table-wrap notation"><table>
  <thead><tr><th>符号</th><th>含义</th><th>形状</th></tr></thead>
  <tbody><tr><td>\(T\)</td><td>序列长度</td><td>标量</td></tr></tbody>
</table></div>
```

## Build & lint
```bash
python3 SKILL_DIR/scripts/build_post.py post/<slug>.src.html      # -> post/<slug>.html
```
Fix every ERROR. Read every WARNING and fix it unless you have a reason not to.
