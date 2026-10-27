#!/usr/bin/env python3
"""build_post.py - turn a post source file into one self-contained HTML page.

    python3 build_post.py my-post.src.html            # writes my-post.html
    python3 build_post.py my-post.src.html -o out.html

What it does (stdlib only, Python 3.8+):
  * <!-- @include figs/x.svg -->  inlines SVG (ids prefixed, styles scoped, size capped
    at natural width), PNG/JPG (base64) or HTML fragments.
  * Numbers <figure id="fig-*">, <figure id="tab-*"> and <div class="eq" id="eq-*">,
    adds caption labels, and an "Illustrative" badge to data-source="illustrative".
  * Resolves cross-references  @fig:name  @tab:name  @eq:name  @sec:name  into links.
  * Resolves citations  [@key]  [@a; @b]  [@key, Table 2]  against
    <ol class="references"><li data-key="key">...</li></ol>, numbers them in order of
    first citation and re-orders the list.
  * Builds the table of contents (<nav id="toc">) from h2/h3, fills reading time.
  * Lints: unresolved refs/citations, template placeholders, TODOs, figures without
    captions or provenance, paper-data figures without a citation, unreferenced
    figures, $...$ inline math (not rendered; use \\( \\)).
Exit status 1 when there are errors (the file is still written so you can inspect it).
"""
import argparse
import base64
import html
import os
import re
import sys

LABELS = {
    "zh": {"fig": "图", "tab": "表", "eq": "式", "toc": "目录", "illus": "示意数据",
           "read": "约 {n} 分钟阅读"},
    "en": {"fig": "Figure", "tab": "Table", "eq": "Eq.", "toc": "Contents",
           "illus": "Illustrative", "read": "{n} min read"},
}

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


# --------------------------------------------------------------------------- includes
def _num(v):
    m = re.match(r"\s*([0-9.]+)\s*(pt|px)?", v or "")
    if not m:
        return None
    x = float(m.group(1))
    return x * 4.0 / 3.0 if m.group(2) == "pt" else x


def clean_svg(text, prefix):
    text = re.sub(r"<\?xml[^>]*\?>", "", text)
    text = re.sub(r"<!DOCTYPE[^>]*>", "", text, flags=re.I)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"<metadata>.*?</metadata>", "", text, flags=re.S)
    m = re.search(r"<svg\b([^>]*)>", text)
    if not m:
        err("include %s: no <svg> root" % prefix)
        return text
    attrs = m.group(1)
    w = re.search(r'\swidth="([^"]+)"', attrs)
    h = re.search(r'\sheight="([^"]+)"', attrs)
    vb = re.search(r'viewBox="([^"]+)"', attrs)
    nat_w = _num(w.group(1)) if w else None
    if not vb and w and h:
        attrs += ' viewBox="0 0 %s %s"' % (re.sub(r"[a-z]+", "", w.group(1)),
                                           re.sub(r"[a-z]+", "", h.group(1)))
    if nat_w is None and vb:
        nat_w = float(vb.group(1).split()[2])
    attrs = re.sub(r'\s(width|height)="[^"]*"', "", attrs)
    attrs = re.sub(r'\sid="[^"]*"', "", attrs)
    style = "max-width:%dpx;" % round(nat_w) if nat_w else ""
    # matplotlib puts a global "*{stroke-linejoin...}" stylesheet in each SVG: scope it
    root_id = prefix + "root"

    def scope_style(sm):
        css = sm.group(2)

        def scope_rule(rm):
            sels = ",".join("#%s %s" % (root_id, s.strip()) for s in rm.group(1).split(","))
            return sels + "{"
        css = re.sub(r"([^{}]+)\{", scope_rule, css)
        return "<style%s>%s</style>" % (sm.group(1), css)
    text = re.sub(r"<style([^>]*)>(.*?)</style>", scope_style, text, flags=re.S)
    if "role=" not in attrs:
        attrs += ' role="img"'
    attrs += ' id="%s"' % root_id
    if style:
        attrs += ' style="%s"' % style
    text = text[:m.start()] + "<svg" + attrs + ">" + text[m.end():]
    # prefix every id so several inlined SVGs never collide
    ids = set(re.findall(r'\sid="([^"]+)"', text)) - {root_id}
    if ids:
        text = re.sub(r'(\sid=")([^"]+)(")',
                      lambda q: q.group(1) + (prefix + q.group(2) if q.group(2) in ids else q.group(2)) + q.group(3), text)
        text = re.sub(r"url\(#([^)]+)\)",
                      lambda q: "url(#%s)" % (prefix + q.group(1) if q.group(1) in ids else q.group(1)), text)
        text = re.sub(r'(href=")#([^"]+)(")',
                      lambda q: q.group(1) + "#" + (prefix + q.group(2) if q.group(2) in ids else q.group(2)) + q.group(3), text)
    return text.strip()


def do_includes(s, base):
    counter = [0]

    def repl(m):
        rel = m.group(1)
        path = os.path.join(base, rel)
        if not os.path.exists(path):
            err("include not found: %s" % rel)
            return m.group(0)
        counter[0] += 1
        ext = os.path.splitext(path)[1].lower()
        if ext == ".svg":
            with open(path, encoding="utf-8") as f:
                return clean_svg(f.read(), "s%d-" % counter[0])
        if ext in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
            mime = {"jpg": "jpeg"}.get(ext[1:], ext[1:])
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            return '<img src="data:image/%s;base64,%s" alt="">' % (mime, b64)
        with open(path, encoding="utf-8") as f:
            return f.read()
    return re.sub(r"<!--\s*@include\s+(\S+)\s*-->", repl, s)


# --------------------------------------------------------------------------- protection
_PROTECT = re.compile(r"<pre\b.*?</pre>|<code\b.*?</code>|<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->",
                      re.S | re.I)


def protect(s):
    store = []

    def repl(m):
        store.append(m.group(0))
        return "\x00%d\x00" % (len(store) - 1)
    return _PROTECT.sub(repl, s), store


def restore(s, store):
    return re.sub(r"\x00(\d+)\x00", lambda m: store[int(m.group(1))], s)


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))


def visible_len(tex):
    """Rough glyph count of the LONGEST row of a LaTeX string (rows split at \\\\;
    commands count as one glyph, \\quad as 1 and \\qquad as 2)."""
    rows = re.split(r"\\\\", tex)
    if len(rows) > 1:
        return max(visible_len(r) for r in rows)
    v = re.sub(r"\\qquad", "XX", tex)
    v = re.sub(r"\\(mathrm|mathbf|text|operatorname|mathit|boldsymbol)\{", "{", v)
    v = re.sub(r"\\(begin|end)\{[a-z*]+\}", "", v)
    v = re.sub(r"\\(left|right|,|;|!|big|Big|bigg|Bigg|displaystyle)", "", v)
    v = re.sub(r"\\[a-zA-Z]+", "X", v)
    return len(re.sub(r"[{}\s]|\\\[|\\\]", "", v))


def attrs_of(tag_attrs):
    return dict(re.findall(r'([\w-]+)="([^"]*)"', tag_attrs))


# --------------------------------------------------------------------------- offline KaTeX
KATEX_VER = "0.16.11"
KATEX_CDN = "https://cdn.jsdelivr.net/npm/katex@%s/dist/" % KATEX_VER
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "academic-blog", "katex-" + KATEX_VER)


def fetch(rel):
    path = os.path.join(CACHE, rel)
    if not os.path.exists(path):
        import urllib.request
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with urllib.request.urlopen(KATEX_CDN + rel, timeout=60) as r:
            data = r.read()
        with open(path, "wb") as f:
            f.write(data)
    with open(path, "rb") as f:
        return f.read()


def inline_katex(s):
    """Replace the KaTeX CDN tags with inline CSS (woff2 fonts as data URIs) and inline JS,
    so math renders with no network. Adds ~0.6 MB."""
    try:
        css = fetch("katex.min.css").decode("utf-8")
        css = re.sub(r"src:url\((fonts/[^)]+?\.woff2)\)[^;}]*",
                     lambda m: 'src:url(data:font/woff2;base64,%s) format("woff2")'
                     % base64.b64encode(fetch(m.group(1))).decode(), css)
        js = fetch("katex.min.js").decode("utf-8")
        ar = fetch("contrib/auto-render.min.js").decode("utf-8")
    except Exception as e:  # noqa: BLE001
        err("--offline: could not download KaTeX (%s); math still loads from the CDN" % e)
        return s
    js, ar = js.replace("</script", "<\\/script"), ar.replace("</script", "<\\/script")
    s = re.sub(r'<link[^>]+katex[^>]+\.css"?[^>]*>', lambda _m: "<style>%s</style>" % css, s, count=1)
    s = re.sub(r'<script[^>]+katex[^>]*/katex\.min\.js"[^>]*></script>', lambda _m: "<script>%s</script>" % js, s, count=1)
    s = re.sub(r'<script[^>]+auto-render\.min\.js"[^>]*></script>', lambda _m: "<script>%s</script>" % ar, s, count=1)
    return s


# --------------------------------------------------------------------------- main passes
def build(src_path, out_path, offline=False):
    with open(src_path, encoding="utf-8") as f:
        s = f.read()
    m = re.search(r'<html[^>]*lang="([^"]+)"', s)
    lang = "zh" if (m and m.group(1).lower().startswith("zh")) else "en"
    L = LABELS[lang]
    nb = " "

    base_dir = os.path.dirname(os.path.abspath(src_path))
    s = do_includes(s, base_dir)
    s, store = protect(s)

    # placeholders / TODOs ------------------------------------------------------
    for ph in sorted(set(re.findall(r"\{\{[A-Za-z][^{}]{0,80}\}\}", s))):
        err("template placeholder left in text: %s" % ph)
    for t in sorted(set(re.findall(r"(\bTODO\b|\bTBD\b|\bFIXME\b|\bXXX\b|lorem ipsum|待补|待定|此处插入)", s, flags=re.I))):
        err("unfinished marker in text: %s" % t)
    for mm in re.finditer(r"(?<![\\$])\$(?!\$)([^$\n<]{1,120}?)(?<!\\)\$(?!\$)", s):
        if re.search(r"[\\_^{}]", mm.group(1)):
            warn("single-dollar math is NOT rendered, use \\( ... \\): $%s$" % mm.group(1)[:40])
            break

    # headings ------------------------------------------------------------------
    heads, sec_n = [], [0]

    def head_repl(m):
        level, attrs, inner = m.group(1), m.group(2), m.group(3)
        a = attrs_of(attrs)
        hid = a.get("id")
        if not hid:
            sec_n[0] += 1
            hid = "sec-%d" % sec_n[0]
            attrs += ' id="%s"' % hid
        if "no-toc" not in a.get("class", ""):
            toc_inner = re.sub(r"<(?!/?(sub|sup|i|em|code)\b)[^>]+>", "", inner).strip()
            heads.append((int(level), hid, strip_tags(inner).strip(), toc_inner, a.get("data-short")))
        return "<h%s%s>%s</h%s>" % (level, attrs, inner, level)
    s = re.sub(r"<h([23])([^>]*)>(.*?)</h\1>", head_repl, s, flags=re.S)
    head_text = {h[1]: (h[4] or h[2]) for h in heads}
    for _, hid, _t, _ti, _sh in heads:
        if not hid.startswith("sec-"):
            warn("heading id '%s' does not start with sec- (cannot be @sec: referenced)" % hid)

    # references to figures before replacement (for "unreferenced" lint)
    ref_uses = re.findall(r"@(fig|tab|eq|sec):([A-Za-z0-9_\-]+)", s)

    # Chinese typography / TL;DR lints ------------------------------------------------
    if lang == "zh":
        am0 = re.search(r"<article\b.*?</article>", s, flags=re.S)
        txt0 = re.sub(r"<[^>]+>", " ", re.sub(r"<svg\b.*?</svg>", " ", am0.group(0) if am0 else s, flags=re.S))
        nq = len(re.findall(r'[\u4e00-\u9fff，。：；]\s*"|"\s*[\u4e00-\u9fff，。]', txt0))
        if nq:
            warn("%d ASCII double quotes next to Chinese text; use full-width “ ” in Chinese sentences" % nq)
    tl = re.search(r'<div class="tldr">(.*?)</div>', s, flags=re.S)
    if tl:
        for li in re.findall(r"<li>(.*?)</li>", tl.group(1), flags=re.S):
            # count measurements, not digits inside names like GQA-8, Llama-2-7B, GSM8K
            nums = re.findall(r"(?<![\w.\-])\d[\d,.]*%?(?![A-Za-z\d\-])", re.sub(r"\\\(.*?\\\)", "", strip_tags(li)))
            if len(nums) > 3:
                warn("TL;DR bullet has %d numbers (aim for one key number): %s" % (len(nums), strip_tags(li)[:50]))

    # figures & tables --------------------------------------------------------------
    numbers = {}
    count = {"fig": 0, "tab": 0}

    def fig_repl(m):
        a = attrs_of(m.group(1))
        body = m.group(2)
        fid = a.get("id", "")
        kind = fid.split("-", 1)[0] if "-" in fid else ""
        if kind not in ("fig", "tab"):
            err("<figure> needs id='fig-...' or id='tab-...' (got %r)" % fid)
            return m.group(0)
        count[kind] += 1
        n = count[kind]
        numbers[fid] = (kind, n)
        dk = a.get("data-kind", "table" if kind == "tab" else "")
        src = a.get("data-source", "")
        capm = re.search(r"<figcaption([^>]*)>(.*?)</figcaption>", body, flags=re.S)
        if not capm:
            err("%s has no <figcaption>" % fid)
            return m.group(0)
        cap_inner = capm.group(2)
        cap_text = strip_tags(cap_inner)
        if dk not in ("data", "diagram", "image", "table", "interactive"):
            err("%s: data-kind must be data | diagram | image | table | interactive" % fid)
        needs_src = dk in ("data", "interactive") or (kind == "tab" and src)
        if needs_src and src not in ("paper", "computed", "illustrative"):
            err("%s: data figures need data-source='paper' | 'computed' | 'illustrative'" % fid)
        if (src == "paper" or dk == "image") and "[@" not in cap_inner:
            err("%s: figure shows numbers/images from a paper but its caption cites nothing ([@key])" % fid)
        if dk == "image":
            warn("%s: raster image from a paper - prefer redrawing from the reported numbers" % fid)
        if a.get("data-script") and not os.path.exists(os.path.join(base_dir, a["data-script"])):
            warn("%s: data-script %s does not exist" % (fid, a["data-script"]))
        cap_len = len(re.findall(r"[\u4e00-\u9fff]", cap_text)) * 2 + len(re.sub(r"[\u4e00-\u9fff\s]", "", cap_text))
        if cap_len < 40:
            warn("%s: caption is very short; state the takeaway and how to read the figure" % fid)
        if not any(k == kind and nm == fid.split("-", 1)[1] for k, nm in ref_uses):
            warn("%s is never referenced in the text (@%s:%s)" % (fid, kind, fid.split("-", 1)[1]))
        label = '<span class="fig-label">%s%s%d</span>' % (L[kind], nb, n)
        badge = '<span class="badge illustrative">%s</span>' % L["illus"] if src == "illustrative" else ""
        new_cap = '<figcaption id="%s-cap"%s>%s%s%s</figcaption>' % (fid, capm.group(1), label, badge, cap_inner)
        body = body[:capm.start()] + new_cap + body[capm.end():]
        body = re.sub(r"<(svg|img)\b(?![^>]*aria-labelledby)", r'<\1 aria-labelledby="%s-cap"' % fid, body, count=1)
        return "<figure%s>%s</figure>" % (m.group(1), body)
    s = re.sub(r"<figure\b([^>]*)>(.*?)</figure>", fig_repl, s, flags=re.S)

    # equations -----------------------------------------------------------------------
    eq_n = [0]

    def eq_repl(m):
        a = attrs_of(m.group(1))
        if "eq" not in a.get("class", "").split() or "id" not in a:
            return m.group(0)
        eq_n[0] += 1
        numbers[a["id"]] = ("eq", eq_n[0])
        name = a["id"].split("-", 1)[1] if "-" in a["id"] else a["id"]
        if not any(k == "eq" and nm == name for k, nm in ref_uses):
            warn("%s is numbered but never referenced (@eq:%s); drop its id or refer to it" % (a["id"], name))
        tex = strip_tags(m.group(2))
        if visible_len(tex) > 50:
            warn("%s has a row of ~%d glyphs; it will crowd the equation number and scroll on phones - "
                 "split it into more rows with aligned/gathered" % (a["id"], visible_len(tex)))
        return '<div%s>%s<span class="eq-num">(%d)</span></div>' % (m.group(1), m.group(2), eq_n[0])
    s = re.sub(r"<div\b([^>]*\bclass=\"eq\"[^>]*)>(.*?)</div>", eq_repl, s, flags=re.S)

    # cross references ------------------------------------------------------------------
    def xref(m):
        kind, name = m.group(1), m.group(2)
        tid = "%s-%s" % (kind, name)
        if kind == "sec":
            if tid not in head_text:
                err("unresolved reference @sec:%s" % name)
                return m.group(0)
            t = head_text[tid]
            if len(t) > (14 if lang == "zh" else 40):
                warn("@sec:%s inserts the whole heading as link text; add data-short=\"...\" to the heading "
                     "or write [short text](@sec:%s)" % (name, name))
            return '<a href="#%s">%s</a>' % (tid, html.escape(t))
        if tid not in numbers:
            err("unresolved reference @%s:%s" % (kind, name))
            return m.group(0)
        n = numbers[tid][1]
        text = ("%s%s(%d)" % (L["eq"], nb, n)) if kind == "eq" else "%s%s%d" % (L[kind], nb, n)
        return '<a href="#%s">%s</a>' % (tid, text)
    def xref_custom(m):
        text, kind, name = m.group(1), m.group(2), m.group(3)
        tid = "%s-%s" % (kind, name)
        if tid not in numbers and tid not in head_text:
            err("unresolved reference [%s](@%s:%s)" % (text, kind, name))
            return m.group(0)
        return '<a href="#%s">%s</a>' % (tid, text)
    s = re.sub(r"\[([^\[\]@]+)\]\(@(fig|tab|eq|sec):([A-Za-z0-9_\-]+)\)", xref_custom, s)
    s = re.sub(r"@(fig|tab|eq|sec):([A-Za-z0-9_\-]+)", xref, s)

    # citations ---------------------------------------------------------------------------
    refm = re.search(r'(<ol class="references"[^>]*>)(.*?)(</ol>)', s, flags=re.S)
    refs = {}
    if refm:
        for km in re.finditer(r'<li\b[^>]*data-key="([^"]+)"[^>]*>(.*?)</li>', refm.group(2), flags=re.S):
            refs[km.group(1)] = km.group(2).strip()
    order = []

    def cite(m):
        parts = []
        for part in re.split(r";", m.group(1)):
            pm = re.match(r"\s*@([\w:.\-]+)\s*(?:,\s*(.+?))?\s*$", part)
            if not pm:
                err("malformed citation [%s]" % m.group(1))
                return m.group(0)
            key, loc = pm.group(1), pm.group(2)
            if key not in refs:
                err("citation key not in reference list: %s" % key)
                parts.append("?")
                continue
            if key not in order:
                order.append(key)
            n = order.index(key) + 1
            title = html.escape(re.sub(r"\s+", " ", strip_tags(refs[key])), quote=True)
            parts.append((n, '<a href="#ref-%s" title="%s">%d</a>%s' % (key, title, n, (", " + loc) if loc else "")))
        parts = [p if isinstance(p, tuple) else (10 ** 9, p) for p in parts]
        return '<span class="cite">[%s]</span>' % ", ".join(h for _, h in sorted(parts, key=lambda q: q[0]))
    s = re.sub(r"\[(@[^\]]+)\]", cite, s)
    if refm:
        uncited = [k for k in refs if k not in order]
        for k in uncited:
            warn("reference '%s' is never cited (kept at end of list)" % k)
        items = "".join('\n  <li id="ref-%s">%s</li>' % (k, refs[k]) for k in order + uncited)
        refm = re.search(r'(<ol class="references"[^>]*>)(.*?)(</ol>)', s, flags=re.S)
        s = s[:refm.start()] + refm.group(1) + items + "\n" + refm.group(3) + s[refm.end():]
    elif re.search(r"\[@", s):
        err("citations used but no <ol class=\"references\"> found")

    # table of contents -----------------------------------------------------------------
    navm = re.search(r'<nav id="toc"([^>]*)>', s)
    if navm and 'data-depth="2"' in navm.group(1):
        heads_toc = [h for h in heads if h[0] == 2]
    else:
        heads_toc = heads
    if sum(1 for h in heads if h[0] == 2) >= 3:
        out, open_sub = ['<div class="toc-title">%s</div><ol>' % L["toc"]], False
        for level, hid, text, toc_inner, _short in heads_toc:
            if level == 2:
                if open_sub:
                    out.append("</ol>")
                    open_sub = False
                out.append('<li><a href="#%s">%s</a>' % (hid, toc_inner))
            else:
                if not open_sub:
                    out.append("<ol>")
                    open_sub = True
                out.append('<li><a href="#%s">%s</a></li>' % (hid, toc_inner))
        if open_sub:
            out.append("</ol>")
        out.append("</ol>")
        toc_html = '<nav id="toc">%s</nav>' % "".join(out)
        s = re.sub(r'<nav id="toc"([^>]*)>\s*</nav>', lambda _m: toc_html.replace("<nav id=\"toc\">", "<nav id=\"toc\"%s>" % _m.group(1), 1), s)

    # reading time ------------------------------------------------------------------------
    am = re.search(r"<article\b.*?</article>", s, flags=re.S)
    body_txt = strip_tags(re.sub(r"<svg\b.*?</svg>|\x00\d+\x00", " ", am.group(0) if am else s, flags=re.S))
    cjk = len(re.findall(r"[一-鿿]", body_txt))
    words = len(re.findall(r"[A-Za-z][A-Za-z'\-]*", body_txt))
    minutes = max(1, round(cjk / 400.0 + words / 230.0))
    rt_html = "<span data-reading-time>%s</span>" % L["read"].format(n=minutes)
    s = re.sub(r"<span data-reading-time>\s*</span>", lambda _m: rt_html, s)

    s = restore(s, store)
    if offline:
        s = inline_katex(s)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(s)

    # report --------------------------------------------------------------------------------
    print("built %s" % out_path)
    print("  figures: %d  tables: %d  numbered equations: %d  references cited: %d  ~%d CJK chars + %d words (%d min)"
          % (count["fig"], count["tab"], eq_n[0], len(order), cjk, words, minutes))
    print("  size: %.0f KB" % (os.path.getsize(out_path) / 1024.0))
    for w in warnings:
        print("  WARNING: " + w)
    for e in errors:
        print("  ERROR: " + e)
    return 1 if errors else 0


def main():
    try:  # Windows consoles default to a legacy code page; keep CJK warnings printable
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("-o", "--out")
    ap.add_argument("--offline", action="store_true",
                    help="inline KaTeX (JS, CSS, fonts) so math renders without network (+~0.6 MB)")
    a = ap.parse_args()
    out = a.out
    if not out:
        base = a.src[:-len(".src.html")] if a.src.endswith(".src.html") else os.path.splitext(a.src)[0] + ".out"
        out = base + ".html"
    sys.exit(build(a.src, out, a.offline))


if __name__ == "__main__":
    main()
