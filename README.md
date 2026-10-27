# academic-blog

A Claude skill for writing AI / ML academic blog posts as a single self-contained HTML page:
rigorous and consistent figures (matplotlib house style + SVG diagram system), KaTeX math,
numbered figures/equations, citations, and a build step that lints provenance and references.

## Install on a new computer

Claude Code reads personal skills from `~/.claude/skills/`. Clone this repo there:

```bash
git clone <this-repo-url> ~/.claude/skills/academic-blog
```

Windows (PowerShell):

```powershell
git clone <this-repo-url> "$env:USERPROFILE\.claude\skills\academic-blog"
```

Update later with `git pull` inside that folder. For claude.ai, upload the packaged
`academic-blog.skill` file under Settings → Capabilities → Skills instead.

## Requirements

- Python 3.8+ (`build_post.py`, `render.py` use only the standard library)
- [uv](https://docs.astral.sh/uv/) to run plot scripts with matplotlib:
  `uv run --with matplotlib --with numpy python plots/x.py`
- Google Chrome, Chromium or Microsoft Edge for previews (`render.py`); set `CHROME=/path` if
  it is not found
- For Chinese figures: a CJK font (macOS PingFang / Windows Microsoft YaHei / Linux
  Noto Sans CJK SC)
- Network once for `build_post.py --offline` (downloads KaTeX into `~/.cache/academic-blog`)

## Layout

- `SKILL.md`: workflow (read by Claude)
- `references/`: writing, data-figure, diagram and HTML-component guides
- `assets/`: page template and an example diagram
- `scripts/`: `blogfig.py` (plot style), `build_post.py` (build + lint), `render.py` (previews)
- `evals/`: test cases used to develop the skill
