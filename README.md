<div align="center">

# 🌐 lumiora.web

**Open your HTML layouts as real desktop apps.**

Frameless, per-pixel-transparent windows — WebView2 rendered through
DirectComposition — with working minimize / maximize / close and
drag-to-move. Pure Python stdlib. Nothing else to install.

```python
import lumiora.web

lumiora.web.demo()              # built-in sample app (two windows)
lumiora.web.run("my-app")       # layout folder -> real desktop app
lumiora.web.serve("my-app")     # same layout -> plain browser server
```

</div>

---

## Why lumiora.web?

Web apps are easy to build, but they live in a browser tab. `lumiora.web`
gives you the same page as a **real desktop window** — like VS Code, not
like a website:

- **Frameless, transparent windows** — the page fills a borderless window at
  exactly the size you designed; rounded corners and glows stay real because
  the window is per-pixel transparent.
- **Working window controls** — hover the top-right corner for minimize /
  maximize / close, or drag anywhere to move the window.
- **The WebView2 runtime ships with Windows 11** — so the desktop app needs
  **no pip packages and no downloads**. The tiny native host embedded in the
  module is pure Python stdlib (ctypes → WebView2 + DirectComposition).
- **Works everywhere anyway** — if WebView2 isn't available, `run()` falls
  back to serving the exact layout in your browser (any OS, zero
  dependencies). `serve()` is the always-browser mode.

This is the same launcher LUMIORA Builder exports embed in its generated
`main.py` — packaged here as a reusable library.

---

## Install

```bash
pip install git+https://github.com/LostZenom/Lumiora.git
```

Python 3.9+. No dependencies.

> **Desktop windows** need Windows 10/11 with the WebView2 runtime (it ships
> with Windows 11 and with current Edge on Windows 10). On any other system
> `lumiora.web.run()` gracefully opens the layout in your browser instead.

---

## Quick start

**Try it — two real windows, no files needed:**

```python
import lumiora.web
lumiora.web.demo()
```

or from the command line:

```bash
python -m lumiora.web --demo
```

**Try the demos in this repo** (real LUMIORA Builder exports):

```bash
git clone https://github.com/LostZenom/Lumiora.git
cd Lumiora

python -m lumiora.web examples                  # opens the Lumiora widget showcase
python -m lumiora.web examples/calculator.py    # opens the calculator demo
```

Both open **exactly like running the export files themselves** — same
windows, same pages, same working minimize / maximize / close. The
calculator is a real, interactive demo: click its keys and it calculates.

You can also run the exports directly:

```bash
python examples/calculator.py   # self-contained — no lumiora install needed
python examples/L.py
```

**Run any exported layout as a desktop app:**

```bash
lumiora.web.run("path/to/exported-app")   # python
python -m lumiora.web path/to/exported-app # CLI
```

**Serve the same layout in the browser:**

```bash
python -m lumiora.web path/to/exported-app --browser
```

The launcher keeps running until you close every window (desktop mode) or
press `Ctrl+C`.

---

## What a layout folder looks like

Point `run()` / `serve()` at any folder with an `index.html`:

```
my-app/
├── index.html      # required — the layout
└── assets/         # optional — images etc. referenced by the page
```

A folder without extra metadata opens as a **single desktop window**, sized
to the layout's design size (the builder stamps `width`/`height` on its
window element; otherwise it defaults to 960×640).

> **Builder exports open exactly like their own `main.py`.** LUMIORA Builder
> downloads a zip containing `main.py` (or `L.py`), `index.html` and
> `run_web.py`. Point `run()` at that folder and it detects the exported
> launcher, reads its embedded per-window desktop pages (parsed with the
> AST — the file is never executed) and opens each one with its real window
> chrome — pixel-identical to running `python main.py` yourself, without
> the giant self-contained file.

### Multi-window apps (`windows.json`)

For true multi-window desktop apps — several windows, each opening on its
own, some staying hidden until a button opens them — add a `windows.json`
manifest:

```json
{
  "title": "My app",
  "windows": [
    { "title": "Login",      "w": 420, "h": 560, "bg": "#0b0d13", "glow": true,  "rounded": true, "hidden": false, "page": "index.html" },
    { "title": "Dashboard",  "w": 900, "h": 600, "bg": "#0b0d13", "glow": false, "rounded": true, "hidden": true,  "page": "dashboard.html" }
  ]
}
```

Field        | Meaning
-------------|------------------------------------------------------------
`title`      | Window title (shown on the taskbar)
`w`, `h`     | Design size in px (transparent margin is added for glow)
`bg`         | Background color behind the page
`glow`       | Add the real outer glow margin
`rounded`    | Rounded transparent corners
`hidden`     | Start closed — opened the first time a `data-lumi-open` button is clicked
`page`       | HTML file for this window (relative to the folder)

A widget/button in one page can open another window by carrying
`data-lumi-open="<index>"` (the window's position in the `windows` array) —
the host keeps that window closed at launch and spawns it on the first click,
like LUMIORA Builder's "open window" action.

---

## CLI reference

```
python -m lumiora.web [folder]            desktop app (WebView2) with browser fallback
python -m lumiora.web [folder] --browser  force the browser server
python -m lumiora.web [folder] --port 8000
python -m lumiora.web --demo              built-in two-window sample
python -m lumiora.web --no-open           don't auto-open the browser fallback
```

---

## How it works

`lumiora.web` is one module (`lumiora/web.py`) that does two things:

1. **A tiny static server** (`127.0.0.1`) that serves each window's page
   (`/win/0`, `/win/1`, …) plus any real files next to the layout.
2. **A native desktop host** that opens each page in its own window: the
   WebView2 runtime is created with a DirectComposition visual target on a
   per-pixel layered (transparent) Win32 window, so the HTML *is* the window
   — rounded corners and glows included. Window controls, drag-to-move and
   the open-window bridge are wired over the WebView2 post-message channel.

The loader (`WebView2Loader.dll`) is written next to the served folder on
first run (or to a temp dir when the folder is read-only).

Every vtable slot and callback in the host comes straight from the WebView2
SDK headers and is verified end-to-end against the real runtime.

---

## Package layout

```
lumiora/
├── __init__.py     # `import lumiora.web`
└── web.py          # the whole launcher: server + WebView2 desktop host
examples/
├── L.py            # the Lumiora widget showcase export
└── calculator.py   # the calculator demo export
pyproject.toml
README.md
```

---

## License

MIT. Lumiora is an independent project — not affiliated with WebView2,
Microsoft or pywebview.
