#!/usr/bin/env python3
"""render.py - look at what you made, with headless Chrome (stdlib only).

    python3 render.py figs/arch.svg          # -> figs/arch.preview.png (2x), styled with the
                                             #    template CSS so the d-* classes work
    python3 render.py post.html              # -> post.page-01.png, post.page-02.png, ...
                                             #    the WHOLE page at desktop width (1440 px), in
                                             #    viewport-sized slices you can open with Read
    python3 render.py post.html --phone      # -> post.phone-01.png ... at a true 390 px viewport,
                                             #    three consecutive screens side by side per image
    python3 render.py post.html --pdf        # -> post.pdf (print layout, for sharing)

Slices are what you review: read every one. Headless Chrome cannot make windows narrower than
~500 px, so --phone loads the post inside a 390 px iframe; media queries then behave like a phone.
Set CHROME=/path/to/chrome if Chrome is not found automatically.
"""
import argparse
import glob
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "assets", "template.html")
CANDIDATES = [
    os.environ.get("CHROME", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
    os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
    os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
    os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge",
]


def chrome():
    for c in CANDIDATES:
        if c and (os.path.exists(c) or shutil.which(c)):
            return c if os.path.exists(c) else shutil.which(c)
    sys.exit("Chrome/Chromium not found; set CHROME=/path/to/chrome")


def url(path):
    """file:// URL that works on macOS, Linux and Windows (file:///C:/...)."""
    return Path(os.path.abspath(path)).as_uri()


def run(args, capture=False):
    base = [chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--no-first-run", "--no-default-browser-check", "--virtual-time-budget=10000",
            "--run-all-compositor-stages-before-draw", "--allow-file-access-from-files"]
    try:
        r = subprocess.run(base + args, stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=180)
    except subprocess.TimeoutExpired:
        print("WARNING: Chrome timed out after 180 s; render the --offline build, which needs "
              "no network for KaTeX")
        return "" if capture else None
    return r.stdout.decode("utf-8", "replace") if capture else None


def tmp_html(content, dirpath):
    fd, path = tempfile.mkstemp(suffix=".html", prefix=".render-", dir=dirpath)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def inject(html_text, script):
    tag = "<script>%s</script>" % script
    return html_text.replace("</body>", tag + "</body>") if "</body>" in html_text else html_text + tag


# ------------------------------------------------------------------------------ SVG preview
def template_head():
    with open(TEMPLATE, encoding="utf-8") as f:
        t = f.read()
    links = "".join(re.findall(r"<link[^>]+>", t))
    style = re.search(r"<style>.*?</style>", t, flags=re.S).group(0)
    return links + style


def render_svg(path, out, scale):
    with open(path, encoding="utf-8") as f:
        svg = f.read()
    svg = re.sub(r"<\?xml[^>]*\?>|<!DOCTYPE[^>]*>", "", svg)
    vb = re.search(r'viewBox="([^"]+)"', svg)
    w, h = 680.0, 400.0
    if vb:
        w, h = [float(v) for v in vb.group(1).split()[2:4]]
        wm = re.search(r'<svg[^>]*\swidth="([0-9.]+)(pt)?"', svg)
        if wm:   # matplotlib: size given in pt
            k = float(wm.group(1)) * (4 / 3.0 if wm.group(2) else 1) / w
            w, h = w * k, h * k
    page = ("<!doctype html><html><head><meta charset='utf-8'>%s</head>"
            "<body style='margin:0;padding:16px;background:#fff'>"
            "<div style='width:%dpx'>%s</div></body></html>") % (template_head(), w, svg)
    t = tmp_html(page, os.path.dirname(os.path.abspath(out)))
    try:
        run(["--force-device-scale-factor=%g" % scale, "--window-size=%d,%d" % (w + 32, h + 32),
             "--screenshot=%s" % os.path.abspath(out), url(t)])
    finally:
        os.unlink(t)
    return [out]


# ------------------------------------------------------------------------------ page slices
MEASURE = ("window.addEventListener('load',function(){setTimeout(function(){"
           "document.documentElement.setAttribute('data-render-h',"
           "Math.ceil(document.documentElement.scrollHeight));},800);});")


def page_height(src_text, dirpath, width):
    t = tmp_html(inject(src_text, MEASURE), dirpath)
    try:
        dom = run(["--window-size=%d,1000" % width, "--dump-dom", url(t)], capture=True)
    finally:
        os.unlink(t)
    m = re.search(r'data-render-h="(\d+)"', dom or "")
    return int(m.group(1)) if m else None


def slices(path, stem, width, height, phone):
    d = os.path.dirname(path)
    with open(path, encoding="utf-8") as f:
        src = f.read()
    for old in glob.glob("%s.%s-*.png" % (stem, "phone" if phone else "page")):
        os.unlink(old)
    vw = 390 if phone else width
    total = page_height(src, d, max(vw, 500))
    if total is None:
        total = height * 6
        print("WARNING: could not measure page height; rendering 6 slices")
    if phone:
        total = int(total * 1.35)   # measured at 500 px; a 390 px layout is taller
    n = max(1, int(math.ceil(total / float(height))))
    per = 3 if phone else 1         # phone: three consecutive screens side by side per image
    outs = []
    for g in range(int(math.ceil(n / float(per)))):
        files, frames = [], []
        for k in range(g * per, min(n, (g + 1) * per)):
            scroll = ("window.addEventListener('load',function(){setTimeout(function(){"
                      "window.scrollTo(0,%d);},600);});" % (k * height))
            inner = tmp_html(inject(src, scroll), d)
            files.append(inner)
            # Scrolling the top-level page does not repaint in headless screenshots, but
            # scrolling inside an iframe does; the iframe also gives a true 390 px viewport.
            frames.append("<iframe src='%s' style='width:%dpx;height:%dpx;border:0;"
                          "background:#fff;flex:none'></iframe>" % (os.path.basename(inner), vw, height))
        wrap = ("<!doctype html><html><body style='margin:0;background:#888;display:flex;gap:16px'>"
                "%s</body></html>") % "".join(frames)
        target = tmp_html(wrap, d)
        files.append(target)
        win_w = max(len(frames) * vw + (len(frames) - 1) * 16, 500)
        out = "%s.%s-%02d.png" % (stem, "phone" if phone else "page", g + 1)
        try:
            run(["--force-device-scale-factor=1", "--window-size=%d,%d" % (win_w, height),
                 "--screenshot=%s" % os.path.abspath(out), url(target)])
        finally:
            for f in files:
                os.unlink(f)
        outs.append(out)
    return outs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("-o", "--out", help="output path (SVG preview or PDF only)")
    ap.add_argument("--pdf", action="store_true", help="HTML: print to PDF instead of slices")
    ap.add_argument("--phone", action="store_true", help="HTML: 390 px phone viewport slices")
    ap.add_argument("--width", type=int, default=1440, help="desktop viewport width")
    ap.add_argument("--height", type=int, default=1400, help="slice height in px")
    ap.add_argument("--scale", type=float, default=2, help="SVG preview pixel ratio")
    a = ap.parse_args()
    f = os.path.abspath(a.file)
    stem, ext = os.path.splitext(f)
    if ext.lower() == ".svg":
        outs = render_svg(f, a.out or stem + ".preview.png", a.scale)
    elif a.pdf:
        out = a.out or stem + ".pdf"
        run(["--no-pdf-header-footer", "--print-to-pdf=%s" % os.path.abspath(out), url(f)])
        outs = [out]
    else:
        outs = slices(f, stem, a.width, a.height, a.phone)
    missing = [o for o in outs if not os.path.exists(o)]
    if missing:
        sys.exit("render failed: %d of %d images not written (%s); retry, or render the "
                 "--offline build" % (len(missing), len(outs), ", ".join(os.path.basename(m) for m in missing)))
    for o in outs:
        print("wrote %s" % o)


if __name__ == "__main__":
    main()
