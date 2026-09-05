#!/usr/bin/env python3
"""LUMIORA Builder export — lumi-calc — runs as a real desktop app via lumiora.web.

    pip install lumiora
    python main.py              # every layout window opens as its own real window

Desktop windows are powered by lumiora.web (WebView2 + DirectComposition,
pure Python stdlib). If lumiora is not installed this falls back to opening
the bundled index.html in your browser — and run_web.py in the same folder
serves it on localhost.

The layout (every window, widget, glow and gooey toggle) is embedded below as
per-window HTML pages and handed to lumiora.web, which opens each one in its
own frameless, per-pixel-transparent window with working minimize / maximize
/ close and drag-to-move. Windows tied to a button action stay closed until
that button is clicked.
"""
import os
import pathlib
import sys
import webbrowser

APP_TITLE = "lumi-calc"
HERE = pathlib.Path(__file__).resolve().parent

# one entry per layout window — each opens as its own real window
WINDOWS = [
    {"title": "Calculator", "w": 340, "h": 480, "bg": "#0c0e14", "glow": True, "rounded": True, "hidden": False}
]

STYLE_CSS = """
/* ============================================================
   LUMIORA Builder — polished dark design system
   ============================================================ */
:root {
  --bg: #0a0d12;
  --bg-deep: #07090d;
  --panel: #10141b;
  --panel2: #151b24;
  --panel3: #1b2230;
  --panel4: #232c3d;
  --border: #202838;
  --border2: #2b3547;
  --border3: #3a465c;
  --text: #e7ecf3;
  --muted: #93a0b4;
  --faint: #5d6b81;
  --accent: #34d399;
  --accent-dim: #10b981;
  --accent-deep: #0b3328;
  --accent-glow: rgba(52, 211, 153, .16);
  --danger: #f87171;
  --warn: #fbbf24;
  --info: #60a5fa;
  --radius: 12px;
  --radius-sm: 8px;
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, .35);
  --shadow: 0 10px 34px rgba(0, 0, 0, .5);
  --shadow-lg: 0 28px 80px rgba(0, 0, 0, .65);
  --font-ui: 'Inter', 'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, 'Cascadia Code', 'SF Mono', Consolas, monospace;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
html, body, #root { height: 100%; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-ui);
  font-size: 13px;
  line-height: 1.45;
  overflow: hidden;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
button, input, select, textarea { font-family: inherit; color: inherit; }
button { cursor: pointer; }
::selection { background: rgba(52, 211, 153, .28); }

/* clean look: no visible scrollbars anywhere — every pane still scrolls
   normally with the wheel / trackpad / touch (and keyboard focus) */
* { scrollbar-width: none; }
::-webkit-scrollbar { width: 0; height: 0; display: none; background: transparent; }

:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }

.app { display: flex; flex-direction: column; height: 100%; }

/* ============================ header ============================ */
.hdr {
  height: 50px; flex: none;
  display: flex; align-items: center; gap: 10px;
  padding: 0 14px;
  background: linear-gradient(180deg, #131823, #10141b);
  border-bottom: 1px solid var(--border);
  z-index: 60;
  position: relative;
}
.hdr::after {
  content: ''; position: absolute; left: 0; right: 0; bottom: -1px; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(52, 211, 153, .5), transparent);
  opacity: .6;
}
.hdr-logo { display: flex; align-items: center; gap: 9px; font-weight: 800; font-size: 14px; letter-spacing: .1px; color: var(--text); }
.hdr-logo .logo {
  width: 30px; height: 30px; border-radius: 9px; object-fit: cover;
  display: block; background: #05070a;
  box-shadow: 0 0 16px rgba(34, 211, 238, .25), 0 2px 8px rgba(0, 0, 0, .5);
}
.hdr-logo .dim { color: var(--accent); }
.hdr-sep { width: 1px; height: 24px; background: var(--border); }
.hdr-group { display: flex; align-items: center; gap: 2px; }
.ibtn {
  width: 30px; height: 30px; display: grid; place-items: center;
  background: transparent; border: 1px solid transparent; border-radius: 8px;
  color: var(--muted); cursor: pointer; transition: all .14s;
}
.ibtn:hover { background: var(--panel3); color: var(--text); border-color: var(--border2); }
/* live preview — the play button next to Export code */
.ibtn.play-live { color: var(--accent); }
.ibtn.play-live:hover {
  background: rgba(52, 211, 153, .1); border-color: rgba(52, 211, 153, .4);
  box-shadow: 0 0 12px rgba(52, 211, 153, .22); color: var(--accent);
}
.ibtn.play-live:disabled { opacity: .3; }
.ibtn:disabled { opacity: .3; cursor: not-allowed; }
.ibtn:disabled:hover { background: transparent; border-color: transparent; color: var(--muted); }
.hdr input.proj-name {
  background: transparent; border: 1px solid transparent; border-radius: 7px;
  color: var(--text); font-size: 13px; font-weight: 600;
  padding: 6px 9px; width: 210px; outline: none; transition: all .15s;
}
.hdr input.proj-name:hover { background: var(--panel2); border-color: var(--border); }
.hdr input.proj-name:focus { background: var(--panel2); border-color: var(--accent-dim); }

.fw-chip {
  background: linear-gradient(180deg, rgba(52, 211, 153, .14), rgba(52, 211, 153, .07));
  color: #34d399;
  border: 1px solid rgba(52, 211, 153, .35); border-radius: 8px;
  padding: 5px 11px; font-size: 12px; font-weight: 700; letter-spacing: .02em;
  white-space: nowrap; user-select: none;
}
.hdr .grow { flex: 1; }

.hdr-btn {
  display: inline-flex; align-items: center; gap: 6px;
  background: var(--panel3); color: var(--text);
  border: 1px solid var(--border2); border-radius: 8px;
  padding: 6px 12px; font-size: 12.5px; font-weight: 600;
  transition: all .15s; white-space: nowrap; user-select: none;
}
.hdr-btn:hover { border-color: var(--accent-dim); color: var(--accent); background: var(--panel4); transform: translateY(-1px); }
.hdr-btn:active { transform: translateY(0); }
.hdr-btn.primary {
  background: linear-gradient(135deg, #34d399, #10b981);
  border-color: transparent; color: #042018; box-shadow: 0 2px 14px rgba(16, 185, 129, .3);
}
.hdr-btn.primary:hover { background: linear-gradient(135deg, #6ee7b7, #34d399); color: #042018; }
/* export code — transparent inside, only the gradient edge shows */
.hdr-btn.export-neon {
  position: relative;
  background: transparent; color: #22d3ee;
  border: none; box-shadow: none;
}
.hdr-btn.export-neon::before {
  content: ''; position: absolute; inset: 0; border-radius: 9px; padding: 1.5px;
  background: linear-gradient(135deg, #22d3ee, #a78bfa);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude;
  pointer-events: none;
}
.hdr-btn.export-neon:hover { background: rgba(34, 211, 238, .09); color: #7de3ff; }
.hdr-btn.export-neon:disabled { opacity: .38; background: transparent; color: #22d3ee; }
.hdr-btn.danger { color: #f8a8a8; }
.hdr-btn.danger:hover { border-color: var(--danger); color: var(--danger); background: #24121a; }
.hdr-btn:disabled { opacity: .38; cursor: not-allowed; transform: none; }
.saved-dot { display: inline-flex; align-items: center; gap: 5px; color: var(--faint); font-size: 11px; }
.saved-dot i { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 6px var(--accent); }

/* ============================ layout ============================ */
.body { flex: 1; display: flex; min-height: 0; }

/* ============================ sidebar ============================ */
.sidebar {
  width: 262px; flex: none;
  background: var(--panel); border-right: 1px solid var(--border);
  display: flex; flex-direction: column; min-height: 0;
}
.sb-tabs { display: flex; gap: 2px; padding: 6px 6px 0; border-bottom: 1px solid var(--border); }
.sb-tab {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 3px;
  padding: 7px 2px 6px; border: none; background: transparent; color: var(--faint);
  border-radius: 8px 8px 0 0; cursor: pointer; font-size: 9.5px; font-weight: 700;
  letter-spacing: .02em; transition: all .15s; position: relative;
}
.sb-tab svg { width: 16px; height: 16px; }
.sb-tab:hover { color: var(--text); background: var(--panel2); }
.sb-tab.active { color: var(--accent); background: linear-gradient(180deg, rgba(52, 211, 153, .1), transparent); }
.sb-tab.active::after {
  content: ''; position: absolute; left: 20%; right: 20%; bottom: -1px; height: 2px;
  background: var(--accent); border-radius: 2px 2px 0 0; box-shadow: 0 -1px 8px var(--accent-glow);
}
.sb-content { flex: 1; overflow-y: auto; overflow-x: hidden; padding: 12px; min-height: 0; }
.sb-section-title {
  font-size: 10px; font-weight: 800; letter-spacing: .1em;
  color: var(--faint); text-transform: uppercase; margin: 2px 2px 9px;
}

.search { position: relative; margin-bottom: 12px; }
.search svg { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); width: 13px; height: 13px; color: var(--faint); pointer-events: none; }
.search input {
  width: 100%; background: var(--panel2); border: 1px solid var(--border);
  border-radius: 9px; color: var(--text); padding: 7px 10px 7px 30px;
  font-size: 12.5px; outline: none; transition: all .15s;
}
.search input:focus { border-color: var(--accent-dim); box-shadow: 0 0 0 3px var(--accent-glow); }

/* palette */
.sb-sec-gap { height: 18px; flex: none; }
.wcard.win-card {
  flex-direction: row; align-items: center; justify-content: flex-start; gap: 11px;
  padding: 8px 11px; margin-bottom: 7px;
}
.wcard.win-card .wicon { width: auto; height: auto; color: var(--muted); }
.wcard.win-card:hover .wicon { color: var(--accent); }
.wcard.win-card .win-txt { display: flex; flex-direction: column; align-items: flex-start; gap: 1px; min-width: 0; }
.wcard.win-card .wsub { font-size: 10px; color: var(--faint); }
.wgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.wcard {
  position: relative;
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  background: var(--panel2); border: 1px solid var(--border);
  border-radius: 11px; padding: 11px 6px 9px;
  cursor: grab; user-select: none; transition: all .16s cubic-bezier(.2,.9,.3,1.2);
}
.wcard:hover {
  border-color: rgba(52, 211, 153, .55); background: var(--panel3);
  transform: translateY(-2px); box-shadow: 0 8px 22px rgba(0,0,0,.35), 0 0 0 1px rgba(52,211,153,.12);
}
.wcard:active { cursor: grabbing; }
.wcard .wicon { width: 100%; height: 34px; display: grid; place-items: center; color: var(--faint); transition: color .15s; }
.wcard:hover .wicon { color: var(--accent); }
.wcard .wname { font-size: 11.5px; font-weight: 600; color: var(--text); }
.wcard .wbadge {
  position: absolute; top: 5px; right: 6px; font-size: 8px; font-weight: 800; letter-spacing: .06em;
  padding: 2px 5px; border-radius: 5px; color: #052318;
  background: linear-gradient(135deg, var(--accent), var(--accent-dim));
  box-shadow: 0 1px 6px rgba(16,185,129,.4);
}
.wcard.plugin .wbadge { color: #2b1a02; background: linear-gradient(135deg, #fbbf24, #f59e0b); box-shadow: 0 1px 6px rgba(245,158,11,.4); }

/* tree */
.tree { user-select: none; padding: 6px 6px 8px; }
/* the window root row — reads as the top of the tree, with a soft
   separator so the widgets hang visibly below it */
.tree-row.root {
  margin-bottom: 4px; padding: 7px 6px; border-radius: 9px;
  background: linear-gradient(180deg, rgba(56,70,94,.28), rgba(30,37,52,.18));
  border: 1px solid rgba(88,105,135,.35);
  font-weight: 700; letter-spacing: .01em;
  box-shadow: 0 1px 0 rgba(0,0,0,.35) inset;
}
.tree-row.root .tname { color: var(--text); }
.tree-row.root .tvar { color: var(--muted); }
.tree-row {
  display: flex; align-items: center; gap: 6px; padding: 5px 8px;
  border-radius: 8px; cursor: pointer; font-size: 12.5px;
  border: 1px solid transparent; transition: background .12s, border-color .12s;
}
.tree-row:hover { background: var(--panel2); }
.tree-row.sel {
  background: linear-gradient(90deg, rgba(34,211,238,.16), rgba(167,139,250,.08));
  border-color: rgba(34,211,238,.38);
}
.tree-row .tname { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--text-soft, var(--text)); }
.tree-row.sel .tname { color: var(--accent); font-weight: 600; }
.tree-row .tvar { font-family: var(--font-mono); font-size: 9.5px; color: var(--faint); white-space: nowrap; }
.tree-row .tdel { visibility: hidden; background: none; border: none; color: var(--muted); cursor: pointer; padding: 1px 4px; border-radius: 5px; font-size: 11px; line-height: 1; }
.tree-row:hover .tdel { visibility: visible; }
.tree-row .tdel:hover { color: var(--accent); background: var(--accent-deep); }
/* kind dots — one glance tells a label from a card from a button */
.tree-row .t-dot {
  width: 7px; height: 7px; border-radius: 3px; flex: none;
  background: #5b6b80;
}
.tree-row .t-dot.win { border-radius: 2.5px; background: linear-gradient(135deg, #34d399, #22d3ee); box-shadow: 0 0 5px rgba(34,211,238,.6); }
.tree-row .t-dot.label { background: #8ab4ff; }
.tree-row .t-dot.btn { background: #34d399; }
.tree-row .t-dot.input { background: #22d3ee; }
.tree-row .t-dot.toggle { background: #a78bfa; }
.tree-row .t-dot.card { background: #f472b6; }
.tree-row .t-dot.img { background: #fbbf24; }
.tree-row .t-dot.other { background: #64748b; }
.tree-caret { width: 14px; flex: none; display: grid; place-items: center; color: var(--faint); transition: transform .12s; border-radius: 4px; }
.tree-caret:hover { color: var(--accent); background: var(--accent-deep); }
.tree-caret.open { transform: rotate(90deg); }
.tree-caret svg { width: 9px; height: 9px; }
.tree-kids { margin-left: 13px; padding-left: 6px; }
.tree-empty { color: var(--faint); font-size: 12px; padding: 14px 8px; text-align: center; line-height: 1.7; }
.tree-row { position: relative; }
.tree-row[draggable="true"] { cursor: grab; }
.tree-row[draggable="true"]:active { cursor: grabbing; }
.tree-guide { position: absolute; left: 0; top: 0; height: 100%; pointer-events: none; opacity: .85; }
.tree.dragging { cursor: grabbing; }
.tree.dragging .tree-row:not(.drag-over) .tname { color: var(--muted); }
.tree-row.drag-over {
  background: rgba(16,185,129,.12);
  box-shadow: inset 0 0 0 1.5px var(--accent);
}
.tree-row.drag-over .tname { color: var(--accent); font-weight: 600; }
.tree-drop-hint {
  margin: 8px 4px 2px; padding: 7px 9px; border-radius: 8px;
  border: 1px dashed var(--accent); background: rgba(16,185,129,.06);
  color: var(--muted); font-size: 11px; line-height: 1.5;
}
.tree-drop-hint b { color: var(--accent); }

/* uploads */
.up-drop {
  border: 1.5px dashed var(--border2); border-radius: var(--radius);
  padding: 20px 10px; text-align: center; color: var(--faint); font-size: 12px;
  cursor: pointer; margin-bottom: 12px; transition: all .15s; background: var(--panel2);
}
.up-drop svg { opacity: .7; }
.up-drop:hover, .up-drop.over { border-color: var(--accent); color: var(--accent); background: var(--accent-deep); }
.up-row {
  display: flex; align-items: center; gap: 8px; padding: 6px 8px;
  border-radius: 9px; border: 1px solid var(--border); margin-bottom: 6px;
  background: var(--panel2); transition: border-color .15s;
}
.up-row:hover { border-color: var(--border3); }
.up-row img { width: 36px; height: 36px; object-fit: cover; border-radius: 7px; background: #000; border: 1px solid var(--border); }
.up-row .un { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 12px; font-weight: 600; }
.up-row .umeta { font-size: 10px; color: var(--faint); margin-top: 1px; }
.up-row .udel { background: none; border: none; color: var(--muted); cursor: pointer; padding: 3px 5px; border-radius: 6px; }
.up-row .udel:hover { color: var(--danger); background: #24121a; }

/* templates */
.tpl-card {
  border: 1px solid var(--border); border-radius: var(--radius);
  overflow: hidden; margin-bottom: 12px; cursor: pointer;
  background: var(--panel2); transition: all .18s cubic-bezier(.2,.9,.3,1.2);
}
.tpl-card:hover { border-color: var(--accent-dim); transform: translateY(-2px); box-shadow: 0 10px 28px rgba(0,0,0,.4); }
.tpl-thumb { height: 96px; position: relative; overflow: hidden; }
.tpl-thumb svg { width: 100%; height: 100%; display: block; }
.tpl-thumb::after {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(180deg, transparent 55%, rgba(16,20,27,.9));
  pointer-events: none;
}
.tpl-info { padding: 9px 12px; display: flex; align-items: center; justify-content: space-between; background: var(--panel2); }
.tpl-info .tn { font-weight: 700; font-size: 12.5px; }
.tpl-info .td { font-size: 10.5px; color: var(--faint); margin-top: 1px; }
.tpl-use { font-size: 10.5px; font-weight: 800; color: var(--accent); opacity: 0; transform: translateX(-4px); transition: all .15s; }
.tpl-card:hover .tpl-use { opacity: 1; transform: none; }

/* ============================ canvas area ============================ */
.canvas-wrap {
  flex: 1; position: relative; overflow: hidden;
  background:
    radial-gradient(1100px 700px at 75% -5%, #0d1620 0%, var(--bg-deep) 55%);
}
.canvas-wrap::before {
  content: ''; position: absolute; inset: 0; pointer-events: none;
  background-image: radial-gradient(rgba(130, 150, 180, .09) 1px, transparent 1.6px);
  background-size: 24px 24px;
}
.canvas-scroll { position: absolute; inset: 0; overflow: auto; }
.canvas-inner { min-width: 100%; min-height: 100%; display: grid; place-items: center; padding: 110px 80px 80px; }
.stage { position: relative; transform-origin: center center; }

/* a window = optional chrome bar + design surface; wrapper sized exactly */
.stage-win { position: relative; }
.stage-win.focused {
  outline: 2px solid rgba(52, 211, 153, .65); outline-offset: 3px;
  border-radius: 13px;
}
.stage-win .win-badge {
  position: absolute; top: -24px; left: 0; z-index: 45;
  background: linear-gradient(135deg, #243042, #1a2130);
  border: 1px solid rgba(52, 211, 153, .5); color: var(--accent);
  font-size: 9.5px; font-weight: 800; letter-spacing: .03em;
  padding: 3px 9px; border-radius: 6px; white-space: nowrap;
  box-shadow: 0 3px 10px rgba(0,0,0,.5); pointer-events: none;
  font-family: var(--font-mono);
}

.window-chrome {
  position: relative; width: 100%; height: 32px; flex: none;
  display: flex; align-items: center; gap: 10px;
  background: linear-gradient(180deg, #1a2130, #141a25);
  border: 1px solid var(--border2); border-bottom: none;
  border-radius: 11px 11px 0 0; padding: 0 14px;
  color: var(--muted); font-size: 11.5px; font-weight: 600;
  box-shadow: 0 -4px 14px rgba(0,0,0,.2);
}
.window-chrome .dots { display: flex; gap: 5px; flex: none; }
.window-chrome .dots i { width: 10px; height: 10px; border-radius: 50%; display: block; }
.window-chrome .dots i:nth-child(1) { background: #ff5f57; }
.window-chrome .dots i:nth-child(2) { background: #febc2e; }
.window-chrome .dots i:nth-child(3) { background: #28c840; }
.window-chrome .wt {
  flex: 1; min-width: 0; text-align: center;
  overflow: hidden; white-space: nowrap; text-overflow: ellipsis;
  color: var(--muted); font-size: 11px; letter-spacing: .02em;
}
.window-chrome.right .wt { text-align: left; }
.window-chrome.right .dots { order: 2; }
/* explicit title position (always wins over the dots-side default above) */
.window-chrome .wt.ta-left { text-align: left; }
.window-chrome .wt.ta-center { text-align: center; }
.window-chrome .wt.ta-right { text-align: right; }

.design-win {
  position: relative;
  background: #23272d;
  border: 1px solid var(--border3);
  overflow: hidden;
  /* strict stacking root: the particle/overlay layers can never blend
     with or reveal anything outside the window (sidebar, canvas, other
     windows) */
  isolation: isolate;
  border-radius: 0 0 10px 10px;
  box-shadow:
    0 0 0 1px rgba(0,0,0,.35),
    0 22px 60px rgba(0,0,0,.55),
    0 2px 8px rgba(0,0,0,.4);
  transition: box-shadow .2s;
}
.design-win.frameless {
  border-radius: 12px;
  border-color: rgba(58,70,92,.55);
  box-shadow:
    0 0 0 1px rgba(0,0,0,.4),
    0 24px 70px rgba(0,0,0,.6),
    0 4px 14px rgba(0,0,0,.35);
}
.design-win.drag-over {
  outline: 2px dashed var(--accent); outline-offset: 6px;
  box-shadow: 0 0 0 4px var(--accent-glow), 0 22px 60px rgba(0,0,0,.55);
}

/* blank start — no windows yet */
.empty-stage {
  position: absolute; inset: 0; z-index: 2;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  text-align: center; padding: 0 24px;
  transition: box-shadow .18s;
}
.empty-stage.over { background: rgba(52, 211, 153, .04); }
.empty-stage .es-icon {
  width: 58px; height: 58px; border-radius: 18px;
  display: grid; place-items: center; color: var(--accent);
  background: linear-gradient(160deg, rgba(52, 211, 153, .16), rgba(52, 211, 153, .05));
  border: 1px solid rgba(52, 211, 153, .35);
  box-shadow: 0 0 34px rgba(52, 211, 153, .18);
}
.empty-stage .es-title { margin-top: 16px; font-size: 19px; font-weight: 800; color: var(--text); }
.empty-stage .es-sub { margin-top: 7px; color: var(--muted); font-size: 12.5px; line-height: 1.8; }
.empty-stage .es-sub b { color: var(--accent); font-weight: 700; }
.empty-stage .es-cards { display: flex; gap: 14px; margin-top: 26px; }
.es-card {
  width: 186px; display: flex; flex-direction: column; align-items: center;
  background: linear-gradient(180deg, #171d27, #12161f);
  border: 1px solid var(--border2); border-radius: 14px;
  padding: 16px 12px 13px; cursor: pointer;
  transition: all .17s cubic-bezier(.2,.9,.3,1.15);
}
.es-card:hover {
  border-color: rgba(52, 211, 153, .6); background: #182029;
  transform: translateY(-3px); box-shadow: 0 12px 30px rgba(0,0,0,.5), 0 0 0 1px rgba(52,211,153,.15);
}
.es-card .es-mini {
  position: relative; width: 108px; height: 66px; border-radius: 8px;
  background: #232a35; border: 1px solid #3a4653; overflow: hidden;
  box-shadow: inset 0 0 0 1px rgba(0,0,0,.3);
}
.es-card .es-mini::after {
  content: ''; position: absolute; left: 0; right: 0; top: 0; height: 17px;
  background: linear-gradient(180deg, #1c2431, #151b26); border-bottom: 1px solid #2e3946;
}
.es-card .es-mini i { position: absolute; top: 5.5px; width: 6px; height: 6px; border-radius: 50%; z-index: 1; }
.es-card .es-mini i.r { left: 7px; background: #ff5f57; }
.es-card .es-mini i.y { left: 16px; background: #febc2e; }
.es-card .es-mini i.g { left: 25px; background: #28c840; }
.es-card .es-mini.plain { border-style: solid; background: linear-gradient(160deg, #161c26, #10141c); }
.es-card .es-mini.plain::after { display: none; }
.es-card .es-mini.plain i { top: 5.5px; }
.es-card .es-mini.top { width: 88px; transform: translate(9px, 4px); opacity: .85; }
.es-card .es-card-name { margin-top: 11px; font-size: 13px; font-weight: 800; color: var(--text); }
.es-card .es-card-sub { margin-top: 2px; font-size: 10.5px; color: var(--faint); }
.empty-stage .es-hint { margin-top: 30px; font-size: 11px; color: var(--faint); }

.frame-grid-overlay {
  position: absolute; inset: 0; pointer-events: none; z-index: 1;
  background-image: linear-gradient(to right, rgba(52,211,153,.14) 1px, transparent 1px),
                    linear-gradient(to bottom, rgba(52,211,153,.14) 1px, transparent 1px);
  background-size: var(--gs, 20px) var(--gs, 20px);
}

.canvas-hint { position: absolute; inset: 0; display: grid; place-items: center; pointer-events: none; z-index: 1; }
.canvas-hint > div { text-align: center; color: var(--faint); font-size: 12px; line-height: 2.1; }
.canvas-hint .big { font-size: 14.5px; color: var(--muted); font-weight: 700; margin-bottom: 2px; letter-spacing: .01em; }

/* ---- widget nodes ---- */
/* VS-style alignment guides — red lines shown while dragging a widget,
   drawn across the whole parent so you see the perfectly-aligned edge */
.align-guides .ag-l {
  position: absolute;
  background: #ff453a;
  z-index: 5;
  box-shadow: 0 0 6px rgba(255, 69, 58, .9), 0 0 1px rgba(255, 69, 58, 1);
}
.align-guides .ag-v { top: 0; bottom: 0; width: 1px; }
.align-guides .ag-h { left: 0; right: 0; height: 1px; }

.wnode { position: absolute; display: flex; }
.wnode.sel-outline {
  outline: 2px solid #22d3ee; outline-offset: 0;
  border-radius: 4px;
  box-shadow: 0 0 0 4px rgba(34,211,238,.25), 0 4px 18px rgba(0,0,0,.3);
}
.wnode.hover-outline:hover { outline: 1.5px solid rgba(52,211,153,.5); outline-offset: 0; border-radius: 4px; }
.wnode.drop-target { outline: 2px dashed var(--warn); outline-offset: 3px; box-shadow: 0 0 0 4px rgba(251,191,36,.12); }

.sel-badge {
  position: absolute; top: -22px; left: -2px; z-index: 31;
  background: linear-gradient(135deg, #22d3ee, #a78bfa);
  color: #0b0d13; font-size: 9.5px; font-weight: 800; letter-spacing: .02em;
  padding: 2.5px 8px; border-radius: 5px 5px 0 0;
  white-space: nowrap; box-shadow: 0 2px 8px rgba(34,211,238,.35);
  pointer-events: none;
}
.sel-badge .badge-dim { opacity: .6; font-weight: 600; }.rh { position: absolute; width: 12px; height: 12px; z-index: 40;
  background: #fff; border: 1.5px solid var(--accent-dim);
  border-radius: 3px; box-shadow: 0 1px 5px rgba(0,0,0,.45);
  opacity: .96; cursor: default;
  touch-action: none;
}
.rh.n { top: -5px; left: calc(50% - 4.5px); cursor: ns-resize; }
.rh.s { bottom: -5px; left: calc(50% - 4.5px); cursor: ns-resize; }
.rh.e { right: -5px; top: calc(50% - 4.5px); cursor: ew-resize; }
.rh.w { left: -5px; top: calc(50% - 4.5px); cursor: ew-resize; }
.rh.nw { top: -5px; left: -5px; cursor: nwse-resize; }
.rh.ne { top: -5px; right: -5px; cursor: nesw-resize; }
.rh.sw { bottom: -5px; left: -5px; cursor: nesw-resize; }
.rh.se { bottom: -5px; right: -5px; cursor: nwse-resize; }

/* floating canvas toolbar */
.float-tb {
  position: absolute; top: 12px; left: 12px; z-index: 50;
  display: flex; align-items: center; gap: 2px;
  background: rgba(19, 24, 33, .92); backdrop-filter: blur(8px);
  border: 1px solid var(--border2); border-radius: 10px; padding: 4px;
  box-shadow: var(--shadow);
}
.ftb-btn {
  width: 28px; height: 28px; display: grid; place-items: center;
  background: transparent; border: none; border-radius: 7px;
  color: var(--muted); cursor: pointer; transition: all .13s;
}
.ftb-btn:hover { background: var(--panel4); color: var(--text); }
.ftb-btn.on { background: var(--accent-deep); color: var(--accent); box-shadow: inset 0 0 0 1px rgba(52,211,153,.35); }
.ftb-btn:disabled { opacity: .3; cursor: not-allowed; }
.ftb-btn:disabled:hover { background: transparent; color: var(--muted); }
.ftb-sep { width: 1px; height: 18px; background: var(--border); margin: 0 3px; }
.zoom-label {
  font-size: 10.5px; color: var(--muted); min-width: 40px; text-align: center;
  font-variant-numeric: tabular-nums; font-weight: 700;
}
.ftb-slider { display: flex; align-items: center; gap: 6px; padding: 0 6px; }
.ftb-slider .lbl { font-size: 10px; color: var(--faint); font-weight: 700; }
input[type='range'] { -webkit-appearance: none; appearance: none; background: transparent; cursor: pointer; }
input[type='range']::-webkit-slider-runnable-track { height: 4px; background: var(--border3); border-radius: 99px; }
input[type='range']::-webkit-slider-thumb {
  -webkit-appearance: none; width: 13px; height: 13px; border-radius: 50%;
  background: var(--accent); margin-top: -4.5px;
  border: 2px solid #0a0d12; box-shadow: 0 0 6px rgba(52,211,153,.5);
}

/* ============================ properties panel ============================ */
.props {
  width: 300px; flex: none;
  background: var(--panel); border-left: 1px solid var(--border);
  display: flex; flex-direction: column; min-height: 0;
}
.props-head {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 10px;
  padding: 13px 16px 11px; border-bottom: 1px solid var(--border);
  background: linear-gradient(180deg, #141a25, transparent);
}
.ph-close {
  flex: none; width: 26px; height: 26px; border-radius: 7px; margin-top: 2px;
  background: none; border: 1px solid var(--border); color: var(--faint);
  cursor: pointer; display: grid; place-items: center;
  transition: all .12s;
}
.ph-close svg { display: block; }
.ph-close:hover { color: var(--text); border-color: var(--accent); background: var(--accent-deep); }
.props-reopen {
  flex: none; width: 34px;
  background: var(--panel); border-left: 1px solid var(--border);
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 7px;
  color: var(--faint); font-size: 10.5px; cursor: pointer; letter-spacing: 1px;
  transition: color .12s;
}
.props-reopen .arw { display: block; color: var(--accent); }
.props-reopen:hover { color: var(--text); }
.props-reopen .pv-label { writing-mode: vertical-rl; }
.props-head .ph-title {
  font-weight: 800; font-size: 13.5px; display: flex; align-items: center; gap: 8px;
}
.props-head .ph-title .kicon { color: var(--accent); display: grid; place-items: center; }
.props-head .ph-sub { color: var(--faint); font-size: 11px; margin-top: 3px; font-family: var(--font-mono); }
.props-body { flex: 1; overflow-y: auto; padding: 4px 16px 20px; min-height: 0; }
.props-empty { color: var(--faint); text-align: center; padding: 46px 24px; font-size: 12.5px; line-height: 1.9; }
.props-empty .big { font-size: 13px; color: var(--muted); font-weight: 700; margin-bottom: 6px; }

.psec { border-bottom: 1px solid var(--border); }
.psec:last-child { border-bottom: none; }
.psec-head {
  width: 100%; display: flex; align-items: center; justify-content: space-between;
  background: none; border: none; color: var(--text); padding: 11px 2px;
  cursor: pointer; font-size: 10.5px; font-weight: 800; letter-spacing: .09em;
  text-transform: uppercase; transition: color .15s;
}
.psec-head:hover { color: var(--accent); }
.psec-head .chev {
  display: grid; place-items: center; width: 16px; height: 16px;
  color: var(--faint); transition: transform .16s;
}
.psec-head.open .chev { transform: rotate(90deg); color: var(--accent); }
.psec-body { padding: 2px 2px 16px; display: flex; flex-direction: column; gap: 11px; }

.prow { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.prow > label { font-size: 12px; color: var(--muted); flex: none; max-width: 44%; font-weight: 500; }
.prow .pctl { flex: 1; display: flex; align-items: center; gap: 6px; justify-content: flex-end; min-width: 0; }
.prow .pctl > * { min-width: 0; }
.pstack { display: flex; flex-direction: column; gap: 7px; }
.pstack > label { font-size: 12px; color: var(--muted); font-weight: 500; }

.pin, .psel, .ptxt {
  background: var(--panel2); border: 1px solid var(--border2); border-radius: 8px;
  color: var(--text); padding: 5.5px 9px; font-size: 12.5px; outline: none; width: 100%;
  transition: all .14s;
}
.pin:focus, .psel:focus, .ptxt:focus { border-color: var(--accent-dim); box-shadow: 0 0 0 3px var(--accent-glow); }
.psel { cursor: pointer; }
.psel option { background: var(--panel3); }
.ptxt { resize: vertical; min-height: 62px; font-family: var(--font-mono); font-size: 11.5px; line-height: 1.55; }
input.pin[type='number'] { width: 70px; }

.color-wrap { display: inline-flex; align-items: center; gap: 7px; }
.color-wrap input[type='color'] {
  -webkit-appearance: none; appearance: none; width: 30px; height: 26px;
  border: 1px solid var(--border2); border-radius: 7px; background: none;
  padding: 2px; cursor: pointer;
}
.color-wrap input[type='color']::-webkit-color-swatch-wrapper { padding: 0; }
.color-wrap input[type='color']::-webkit-color-swatch { border: none; border-radius: 4px; }
.color-wrap .hex { font-family: var(--font-mono); font-size: 10.5px; color: var(--faint); width: 74px; }
.color-wrap .hex input {
  width: 100%; background: var(--panel2); border: 1px solid var(--border2);
  border-radius: 6px; color: var(--text); padding: 3px 6px; font-size: 11px;
  outline: none; font-family: var(--font-mono);
}
.color-wrap .hex input:focus { border-color: var(--accent-dim); }
/* the ⊗ "clear — use theme color" button: quiet ghost, transparent fill */
.clr-btn { display: none; }

/* REAL gooey toggle — the exact same iOS-style gooey switch as the exported
   ToggleBox widget (see WidgetPreview.tsx for the reference SVG): a dented
   pill track, a big white blob knob whose three rects merge through the goo
   filter (feGaussianBlur + alpha contrast) into one melting pill as it
   slides across, a pause-bar when on and a soft ring hint when off. Each
   instance embeds its own filter so the goo never bleeds across toggles. */
.switch { position: relative; width: 44px; height: 21px; flex: none; display: inline-block; vertical-align: middle; cursor: pointer; --goo-on: var(--accent, #22d3ee); }
.switch input { opacity: 0; width: 0; height: 0; position: absolute; }
.switch .goo-svg { width: 100%; height: 100%; overflow: visible; display: block; }
.switch .goo-track { fill: #d3d3d6; transition: fill .35s ease; }
.switch.on .goo-track { fill: var(--goo-on); filter: drop-shadow(0 0 5px color-mix(in srgb, var(--goo-on) 55%, transparent)); }
/* the wide knob rect — stretches and slides; the big circles pop in/out at
   each end so the blob looks like it melts from circle to pill */
.switch .goo-knob-center { transform-origin: center; transition: transform .55s cubic-bezier(.3, 1.25, .45, 1); }
.switch.on .goo-knob-center { transform: translateX(150px); }
.switch .goo-knob { transform-origin: center; backface-visibility: hidden; transition: transform .42s cubic-bezier(.3, 1.4, .5, 1); }
.switch .goo-knob.left { transform: scale(1); }
.switch.on .goo-knob.left { transform: scale(0); }
.switch .goo-knob.right { transform: scale(0); }
.switch.on .goo-knob.right { transform: scale(1); }
/* pause-bar (on) and ring hint (off) — the knob slides over them */
.switch .goo-icon { transition: fill .35s ease; }
.switch .goo-icon.on { fill: #c6c6cb; }
.switch.on .goo-icon.on { fill: #fff; }
.switch .goo-icon.off { fill: #eaeaec; }
.switch.on .goo-icon.off { fill: var(--goo-on); }

.icon-btn {
  width: 24px; height: 24px; flex: none; display: grid; place-items: center;
  background: transparent; border: none; color: var(--muted);
  cursor: pointer; border-radius: 6px; transition: all .13s;
}
.icon-btn:hover { color: var(--text); background: var(--panel3); }
.icon-btn.danger:hover { color: var(--danger); background: #24121a; }
/* widget actions — a quiet "+ Action" chip that opens the picker on click */
.act-row { display: flex; margin: 6px 0 2px; }
.act-add {
  display: inline-flex; align-items: center;
  background: transparent; color: var(--muted);
  border: 1px dashed var(--border3); border-radius: 8px;
  padding: 5px 12px; font-size: 11px; font-weight: 700; letter-spacing: .04em;
  cursor: pointer; transition: all .14s;
}
.act-add:hover { color: var(--accent); border-color: var(--accent-dim); background: var(--accent-deep); }
.act-card {
  margin: 6px 0 2px; border: 1px solid var(--border2); border-radius: 10px;
  background: var(--panel2); padding: 8px 10px 4px;
}
.act-card .hint-note { margin-top: 2px; }
.act-head { display: flex; align-items: center; justify-content: space-between; }
.act-title {
  font-size: 10px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase;
  color: var(--accent); padding-bottom: 4px;
}
.act-card .prow { margin: 0; }
/* the two-mode segmented picker inside the card */
.oc-seg {
  display: flex; gap: 3px; background: var(--panel3);
  border: 1px solid var(--border); border-radius: 9px; padding: 3px;
  margin: 2px 0 10px;
}
.oc-opt {
  flex: 1; border: none; background: transparent; color: var(--muted);
  font-size: 11px; font-weight: 700; padding: 5px 4px; border-radius: 6px;
  cursor: pointer; transition: all .14s;
}
.oc-opt:hover { color: var(--text); }
.oc-opt.on {
  background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 26%, transparent), color-mix(in srgb, var(--accent) 10%, transparent));
  color: var(--accent); box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--accent) 45%, transparent);
}
.act-card .ptxt { width: 100%; }
.act-card .hint-note code { color: var(--accent); font-family: var(--font-mono); font-size: 10.5px; }
.icon-btn a { display: contents; }

.optlist { display: flex; flex-direction: column; gap: 6px; }
.optlist-row { display: flex; align-items: center; gap: 6px; }
.optlist-row .pin { flex: 1; }

.asset-pick { display: flex; align-items: center; gap: 8px; }
.asset-pick .thumb { width: 42px; height: 30px; border-radius: 6px; background: #000 center/cover; border: 1px solid var(--border2); }
.asset-pick .an { flex: 1; font-size: 11.5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--muted); }

.seg { display: inline-flex; background: var(--panel2); border: 1px solid var(--border2); border-radius: 8px; padding: 2px; gap: 2px; }
.seg {
  display: inline-flex; background: transparent;
  border: 3px solid linear-gradient(90deg, #22d3ee, #a78bfa);
  border-radius: 8px; padding: 3px; gap: 2px;
}
.seg button {
  border: none; background: transparent; color: rgba(255,255,255,.7);
  font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 7px; cursor: pointer;
  transition: all .13s;
}
.seg button:hover { color: #fff; }
.seg button.on {
  background: rgba(255,255,255,.95); color: #0b0d13;
  box-shadow: 0 0 0 1px rgba(255,255,255,.25);
}

.ev-row { display: flex; align-items: center; gap: 6px; }
.ev-row .psel { flex: 1; }

.props-footer {
  border-top: 1px solid var(--border); padding: 10px 16px;
  display: flex; gap: 8px; background: var(--panel);
}
.props-footer .hdr-btn { flex: 1; justify-content: center; }

/* ============================ export / code modal ============================ */
.modal-overlay {
  position: fixed; inset: 0; z-index: 200;
  background: rgba(4, 6, 10, .78); backdrop-filter: blur(6px);
  display: grid; place-items: center; animation: fadeIn .16s ease;
}
@keyframes fadeIn { from { opacity: 0; } }
.modal {
  background: linear-gradient(180deg, #141a24, #10141b);
  border: 1px solid var(--border2); border-radius: 16px;
  width: min(1080px, calc(100vw - 56px)); max-height: calc(100vh - 72px);
  display: flex; flex-direction: column;
  box-shadow: var(--shadow-lg); animation: popIn .2s cubic-bezier(.2,.9,.3,1.2);
}
@keyframes popIn { from { transform: scale(.965) translateY(8px); opacity: 0; } }
.modal-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 15px 20px; border-bottom: 1px solid var(--border);
}
.modal-head .mt { font-weight: 800; font-size: 15px; display: flex; align-items: center; gap: 10px; }
.modal-head .mt svg { color: #22d3ee; }
.modal-head .ms { color: var(--faint); font-size: 11.5px; margin-top: 3px; }
.modal-x {
  background: none; border: none; color: var(--muted); cursor: pointer;
  padding: 5px 9px; border-radius: 8px; transition: all .13s;
}
.modal-x:hover { color: var(--text); background: var(--panel3); }
.modal-body { padding: 16px 20px; overflow: auto; min-height: 0; }
.modal-foot {
  padding: 13px 20px; border-top: 1px solid var(--border);
  display: flex; gap: 8px; justify-content: flex-end; align-items: center;
}

.exp-grid { display: grid; grid-template-columns: 218px 1fr; gap: 16px; }
.exp-files {
  background: var(--panel2); border: 1px solid var(--border);
  border-radius: 11px; padding: 6px; align-self: start; position: sticky; top: 0;
}
.exp-file-row {
  display: flex; align-items: center; gap: 8px; padding: 7.5px 10px;
  border-radius: 8px; cursor: pointer; font-family: var(--font-mono);
  font-size: 12px; color: var(--muted); border: 1px solid transparent;
  transition: all .13s;
}
.exp-file-row svg { color: var(--faint); }
.exp-file-row:hover { background: var(--panel3); }
.exp-file-row.on {
  background: linear-gradient(135deg, rgba(34,211,238,.18), rgba(167,139,250,.08));
  border-color: rgba(34,211,238,.45); color: #22d3ee;
  box-shadow: 0 0 12px rgba(34,211,238,.18);
}
.exp-file-row.on svg { color: #22d3ee; }
.exp-file-row .fn { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.exp-file-row .fsize { font-size: 9.5px; opacity: .65; }
.exp-file-row.webapp { border-color: rgba(52, 211, 153, .28); }
.exp-file-row.webapp svg { color: var(--accent); }
.exp-file-row .webapp-tag {
  flex: none; font-size: 9px; font-weight: 800; letter-spacing: .05em;
  text-transform: uppercase; color: #042018;
  background: linear-gradient(135deg, #34d399, #22d3ee);
  border-radius: 5px; padding: 1.5px 6px;
}
.exp-main {
  display: flex; flex-direction: column; min-width: 0; min-height: 430px;
  border: 1px solid var(--border); border-radius: 11px; overflow: hidden;
  background: #0a0d13;
}
.exp-code {
  flex: 1; overflow: auto; font-family: var(--font-mono); font-size: 12.5px;
  line-height: 1.6; padding: 13px 0;
}
.exp-code.with-gutter { display: grid; grid-template-columns: auto 1fr; }
.exp-code .ln {
  color: #33405a; text-align: right; padding: 0 14px 0 16px; user-select: none;
  font-size: 11px; line-height: 1.6;
}
.code-plain {
  font: inherit; color: #c9d6e8; white-space: pre; tab-size: 4;
  padding-right: 20px; overflow: visible;
  word-wrap: normal; overflow-wrap: normal;
}
.exp-code.with-gutter .code-plain {
  display: block;
}
.code-plain .py-k { color: #ffcb6b; }
.code-plain .py-c { color: #5d6b81; font-style: italic; }
.code-plain .py-s { color: #9cdcfe; }
.code-plain .py-f { color: #d2a8ff; }
.code-plain .py-n { color: #b5cea8; }
.exp-file-row .fn, .exp-file-row .fsize { white-space: nowrap; }
.exp-note {
  font-size: 11.5px; color: var(--faint); padding: 10px 2px 0; line-height: 1.7;
}
.exp-note code {
  background: var(--panel2); border: 1px solid var(--border);
  padding: 1px 6px; border-radius: 5px; font-family: var(--font-mono); font-size: 10.5px;
  color: var(--accent);
}
.exp-actions { display: flex; gap: 8px; }

/* ============================ toasts ============================ */
.toasts {
  position: fixed; bottom: 18px; right: 18px; z-index: 400;
  display: flex; flex-direction: column; gap: 8px; pointer-events: none;
}
.toast {
  pointer-events: auto;
  background: linear-gradient(180deg, #1a2130, #141a25);
  border: 1px solid var(--border2);
  border-left: 3px solid var(--accent);
  border-radius: 10px; padding: 11px 15px; min-width: 250px; max-width: 400px;
  font-size: 12.5px; box-shadow: var(--shadow);
  animation: toastIn .22s cubic-bezier(.2,.9,.3,1.15); cursor: pointer;
}
.toast::before { content: ''; display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--accent); margin-right: 9px; box-shadow: 0 0 8px var(--accent); }
.toast.error { border-left-color: var(--danger); } .toast.error::before { background: var(--danger); box-shadow: none; }
.toast.warn { border-left-color: var(--warn); } .toast.warn::before { background: var(--warn); box-shadow: none; }
.toast.info { border-left-color: var(--info); } .toast.info::before { background: var(--info); box-shadow: none; }
@keyframes toastIn { from { transform: translateX(34px); opacity: 0; } }

/* ============================ context menu ============================ */
.ctx-menu {
  position: fixed; z-index: 500; min-width: 190px;
  background: linear-gradient(180deg, #1a2130, #141a25);
  border: 1px solid var(--border2); border-radius: 11px; padding: 5px;
  box-shadow: var(--shadow-lg); animation: fadeIn .12s ease;
}
.ctx-item {
  display: flex; align-items: center; gap: 9px; width: 100%; text-align: left;
  background: none; border: none; color: var(--text); font-size: 12.5px;
  padding: 7.5px 11px; border-radius: 7px; cursor: pointer; transition: all .12s;
}
.ctx-item:hover { background: var(--accent-deep); color: var(--accent); }
.ctx-item.danger { color: #f0a0a0; }
.ctx-item.danger:hover { background: #2b1419; color: var(--danger); }
.ctx-item .ck { margin-left: auto; font-size: 10px; color: var(--faint); }
.ctx-sep { height: 1px; background: var(--border); margin: 4px 8px; }
.ctx-item:disabled { opacity: .4; cursor: not-allowed; }

/* ============================ widget previews (canvas tk look) ============================ */
.tk-label {
  display: flex; align-items: center; justify-content: center;
  width: 100%; height: 100%; text-align: center; overflow: hidden;
  padding: 2px 6px; user-select: none; white-space: nowrap;
}
.tk-btn {
  background: #2d333b; border: 1px solid #3f4a58; color: #e7ecf3;
  border-radius: 5px; display: flex; align-items: center; justify-content: center;
  overflow: hidden; width: 100%; height: 100%; text-align: center;
  padding: 2px 8px; user-select: none; white-space: nowrap;
  box-shadow: inset 0 -1px 0 rgba(0,0,0,.2), inset 0 1px 0 rgba(255,255,255,.07);
  text-shadow: 0 1px 1px rgba(0,0,0,.2);
}
.tk-input {
  background: #161b22; border: 1px solid #39424f; border-radius: 5px;
  color: #e7ecf3; padding: 0 9px; width: 100%; height: 100%;
  display: flex; align-items: center; font-size: 12px;
  box-shadow: inset 0 2px 3px rgba(0,0,0,.35);
}
.tk-input input { background: transparent; border: none; outline: none; color: inherit; width: 100%; height: 100%; font-size: inherit; font-family: inherit; }
.tk-text { width: 100%; height: 100%; display: flex; }
.tk-text textarea {
  width: 100%; height: 100%; background: #161b22; border: 1px solid #39424f;
  border-radius: 5px; color: #e7ecf3; font-size: 12px; padding: 6px 9px;
  resize: none; outline: none; font-family: inherit; line-height: 1.5;
  box-shadow: inset 0 2px 3px rgba(0,0,0,.3);
}
.tk-check { display: flex; align-items: center; gap: 8px; width: 100%; height: 100%; padding: 0 5px; overflow: hidden; }
.tk-check .box {
  width: 15px; height: 15px; border: 1.5px solid #55606f; border-radius: 4px;
  background: #161b22; display: grid; place-items: center; flex: none;
}
.tk-check .box.on { background: var(--accent-dim); border-color: var(--accent-dim); box-shadow: 0 0 6px rgba(16,185,129,.4); }
.tk-check .box.on::after { content: ''; width: 8px; height: 4.5px; border-left: 2.2px solid #042018; border-bottom: 2.2px solid #042018; transform: rotate(-45deg) translateY(-1px); }
.tk-check .txt { font-size: 12px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.tk-radio { display: flex; align-items: center; gap: 8px; width: 100%; height: 100%; padding: 0 5px; }
.tk-radio .dot {
  width: 15px; height: 15px; border: 1.5px solid #55606f; border-radius: 50%;
  background: #161b22; display: grid; place-items: center; flex: none;
}
.tk-radio .dot.on { border-color: var(--accent); box-shadow: 0 0 6px rgba(52,211,153,.4); }
.tk-radio .dot.on::after { content: ''; width: 7px; height: 7px; border-radius: 50%; background: var(--accent); }
.tk-radio .txt { font-size: 12px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.tk-slider { width: 100%; height: 100%; display: flex; align-items: center; padding: 0 8px; }
.tk-slider .track { position: relative; flex: 1; height: 5px; background: #2c3540; border-radius: 99px; box-shadow: inset 0 1px 2px rgba(0,0,0,.4); }
.tk-slider .fill { position: absolute; left: 0; top: 0; bottom: 0; background: linear-gradient(90deg, var(--accent-dim), var(--accent)); border-radius: 99px; }
.tk-slider .knob { position: absolute; top: 50%; width: 15px; height: 15px; background: #e9eef5; border-radius: 50%; transform: translate(-50%, -50%); border: 2px solid var(--accent-dim); box-shadow: 0 1px 4px rgba(0,0,0,.4); }
.tk-dropdown { position: relative; width: 100%; height: 100%; }
.tk-dropdown .dd-head {
  width: 100%; height: 100%; display: flex; align-items: center;
  padding: 0 10px; gap: 6px; user-select: none;
  background: #2a313c; border: 1px solid #414c5a; border-radius: 5px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.06);
}
.tk-dropdown .dd-head .car { margin-left: auto; font-size: 8px; color: #8b95a8; }
.tk-progress { width: 100%; height: 100%; display: flex; align-items: center; padding: 0 4px; }
.tk-progress .tr {
  flex: 1; height: 11px; background: #14181f; border: 1px solid #38424e;
  border-radius: 99px; overflow: hidden; box-shadow: inset 0 1px 3px rgba(0,0,0,.5);
}
.tk-progress .fl { height: 100%; background: repeating-linear-gradient(-45deg, var(--accent-dim) 0 8px, #0d9e6e 8px 16px); }
.tk-canvasw { width: 100%; height: 100%; background: #161b22; border: 1px solid #39424f; border-radius: 4px; position: relative; overflow: hidden; }
.tk-canvasw .fake-shapes { position: absolute; inset: 0; opacity: .55; }
.tk-sep { width: 100%; height: 100%; display: flex; align-items: center; }
.tk-sep .ln { flex: 1; height: 2px; background: repeating-linear-gradient(90deg, #3c4654 0 6px, transparent 6px 10px); border-radius: 2px; }

.tk-map {
  width: 100%; height: 100%;
  background: linear-gradient(160deg, #17222d 0%, #101722 60%, #0d131c 100%);
  position: relative; overflow: hidden;
}
.tk-map .gridlines { position: absolute; inset: 0; background-image: linear-gradient(to right, rgba(60,80,100,.18) 1px, transparent 1px), linear-gradient(to bottom, rgba(60,80,100,.18) 1px, transparent 1px); background-size: 24px 24px; }
.tk-map .pin-icon { position: absolute; left: 46%; top: 34%; font-size: 22px; filter: drop-shadow(0 3px 5px rgba(0,0,0,.6)); }
.tk-map .zoom-ctl { position: absolute; right: 7px; bottom: 7px; display: flex; flex-direction: column; gap: 3px; }
.tk-map .zoom-ctl i { width: 20px; height: 20px; background: #1d2833; border: 1px solid #35434f; border-radius: 5px; display: grid; place-items: center; font-size: 12px; color: #8fa2b5; font-style: normal; }
.tk-map .attr { position: absolute; right: 8px; bottom: 2px; font-size: 8px; color: rgba(140,160,180,.5); font-family: var(--font-mono); }
.tk-time {
  width: 100%; height: 100%; display: grid; place-items: center;
  background: radial-gradient(circle at 50% 40%, #182232, #0c1219 75%);
  border: 1px solid #2c3947; border-radius: 50%; position: relative;
}
.tk-time .face { position: relative; width: 76%; height: 76%; border: 2px solid #2c3947; border-radius: 50%; background: radial-gradient(circle, #131c28, #0d141d); }
.tk-time .face i { position: absolute; left: 50%; top: 4%; width: 1.5px; height: 8%; background: #46556a; transform-origin: 50% 100%; }
.tk-time .hands { position: absolute; left: 50%; top: 50%; width: 2.5px; height: 30%; background: linear-gradient(180deg, var(--accent), var(--accent-dim)); transform-origin: 50% 100%; transform: translate(-50%, -100%) rotate(120deg); border-radius: 2px; box-shadow: 0 0 6px rgba(52,211,153,.5); }
.tk-time .center { position: absolute; left: 50%; top: 50%; width: 7px; height: 7px; background: #e9eef5; border-radius: 50%; transform: translate(-50%, -50%); box-shadow: 0 0 8px rgba(0,0,0,.6); }
.tk-video { width: 100%; height: 100%; background: #000; display: flex; flex-direction: column; border: 1px solid #222a33; border-radius: 5px; overflow: hidden; }
.tk-video .screen { flex: 1; display: grid; place-items: center; color: #4b5563; background: radial-gradient(circle at 50% 40%, #0f1419, #000); }
.tk-video .screen .pb {
  width: 46px; height: 46px; border-radius: 50%; border: 2px solid #2b3440;
  display: grid; place-items: center; font-size: 16px; color: #5f6f80; padding-left: 3px;
}
.tk-video .bar { height: 28px; background: #0b0f13; border-top: 1px solid #1a212a; display: flex; align-items: center; gap: 9px; padding: 0 10px; color: #56626f; font-size: 10px; font-family: var(--font-mono); }
.tk-video .bar .tr { flex: 1; height: 3px; background: #232b34; border-radius: 2px; }
.tk-table { width: 100%; height: 100%; display: grid; grid-template-rows: auto 1fr; background: #0e1218; border: 1px solid #333d49; border-radius: 5px; overflow: hidden; }
.tk-table .th { display: grid; grid-template-columns: repeat(4, 1fr); background: #182030; border-bottom: 1px solid #283040; }
.tk-table .th div { padding: 4px 7px; font-size: 10px; font-weight: 800; color: var(--accent); border-right: 1px solid #222b38; }
.tk-table .tbody { overflow: hidden; }
.tk-table .trr { display: grid; grid-template-columns: repeat(4, 1fr); border-bottom: 1px solid #161c26; }
.tk-table .trr div { padding: 3.5px 7px; font-size: 10px; color: #93a1b5; }

.tk-spinbox { display: flex; width: 100%; height: 100%; }
.tk-spinbox .v { flex: 1; display: flex; align-items: center; padding: 0 9px; font-size: 12px; background: #161b22; border: 1px solid #39424f; border-radius: 5px 0 0 5px; }
.tk-spinbox .btns { display: flex; flex-direction: column; width: 20px; }
.tk-spinbox .btns button { flex: 1; background: #232b36; border: 1px solid #39424f; color: #8b95a8; font-size: 8px; display: grid; place-items: center; cursor: default; }
.tk-spinbox .btns button:first-child { border-left: none; border-bottom: none; border-radius: 0 5px 0 0; }
.tk-spinbox .btns button:last-child { border-left: none; border-radius: 0 0 5px 0; }

/* ============================ custom widgets library ============================ */
.cw-editor {
  background: var(--panel2); border: 1px solid var(--border2); border-radius: 11px;
  padding: 11px; margin-bottom: 12px; display: flex; flex-direction: column; gap: 6px;
}
.cw-editor .cw-l { font-size: 10.5px; color: var(--muted); font-weight: 600; margin-top: 2px; }
.cw-editor .cw-l code {
  font-family: var(--font-mono); font-size: 9.5px; background: var(--panel3);
  border: 1px solid var(--border); border-radius: 4px; padding: 0 4px; color: var(--accent);
}
.cw-editor .cw-code { min-height: 150px; }
.cw-card { cursor: grab; transition: border-color .15s, background .15s; }
.cw-card:hover { border-color: rgba(52, 211, 153, .45); }
.cw-card:active { cursor: grabbing; }
.cw-card .cw-icon { width: 34px; height: 30px; display: grid; place-items: center; color: var(--accent); background: var(--accent-deep); border-radius: 7px; flex: none; }

/* ============================ lumiora-style capsule slider ============================ */
.tk-slider.lux { padding: 0; }
.tk-slider.lux .track {
  height: 16px; border-radius: 99px;
  background: #20262f; border: 1px solid #39424f;
  box-shadow: inset 0 1.5px 3px rgba(0,0,0,.5), inset 0 0 0 1px rgba(255,255,255,.02);
  overflow: visible;
}
.tk-slider.lux .fill {
  top: 1px; bottom: 1px; left: 1px;
  background: linear-gradient(90deg, #0ea472, #34d399);
  box-shadow: 0 0 10px rgba(52, 211, 153, .35);
}
.tk-slider.lux .fill-readout {
  position: absolute; top: 50%;
  transform: translate(calc(-100% - 8px), -50%);
  font-size: 9.5px; font-weight: 800; color: #041a11;
  letter-spacing: .02em; pointer-events: none;
}
.tk-slider.lux .knob {
  width: 18px; height: 18px; background: #f2f6fb; border: 2.5px solid #0ea472;
  box-shadow: 0 1px 5px rgba(0,0,0,.45), 0 0 0 3px rgba(52,211,153,.18);
}

/* ============================ lumiora widget previews (canvas) ============================ */
/* every color follows the project accent + theme via --lumi-* vars, so the
   canvas preview is exactly the exported app */
.lumi-pv { width: 100%; height: 100%; display: block; }
.lumi-pv.t-light {
  --lumi-surface: #ffffff; --lumi-surface2: #f2f4f8;
  --lumi-text: #1c1e26; --lumi-sub: #666c7a; --lumi-border: #dfe2ea;
  --lumi-track: #eceef3; --lumi-fillink: #1c1e26;
}
.lumi-pv.t-dark {
  --lumi-surface: #1c1e24; --lumi-surface2: #20252e;
  --lumi-text: #f5f5f7; --lumi-sub: #9b9fa8; --lumi-border: #2e313a;
  --lumi-track: #20242c; --lumi-fillink: #ffffff;
}
/* the iOS-style gooey toggle — the reference SVG: pill track, sliding
   gooey white knob (pause-bar when on, ring hint when off) */
.lumi-goo {
  --goo-off: #d3d3d6;
  --goo-on: var(--lumi-accent);
  position: relative; width: 100%; height: 100%;
}
.lumi-goo svg.goo-svg { width: 100%; height: 100%; overflow: visible; display: block; }
.lumi-goo .goo-track { fill: var(--goo-off); transition: fill .4s; }
.lumi-goo.on .goo-track { fill: var(--goo-on); filter: drop-shadow(0 0 5px color-mix(in srgb, var(--goo-on) 55%, transparent)); }
.lumi-goo .goo-knob-center { transform-origin: center; transition: transform .6s; }
.lumi-goo.on .goo-knob-center { transform: translateX(150px); }
.lumi-goo .goo-knob { transform-origin: center; backface-visibility: hidden; transition: transform .45s; }
.lumi-goo .goo-knob.left { transform: scale(1); }
.lumi-goo.on .goo-knob.left { transform: scale(0); }
.lumi-goo .goo-knob.right { transform: scale(0); }
.lumi-goo.on .goo-knob.right { transform: scale(1); }
.lumi-goo .goo-icon { transition: fill .4s; }
.lumi-goo .goo-icon.on { fill: var(--goo-off); }
.lumi-goo.on .goo-icon.on { fill: #fff; }
.lumi-goo .goo-icon.off { fill: #eaeaec; }
.lumi-goo.on .goo-icon.off { fill: var(--goo-on); }
.lumi-check { display: flex; align-items: center; gap: 8px; width: 100%; height: 100%; padding: 0 2px; }
.lumi-check .box {
  width: 15px; height: 15px; border-radius: 5px; flex: none;
  border: 1.5px solid #55606f; background: #161b22; display: grid; place-items: center;
  box-shadow: inset 0 1px 2px rgba(0,0,0,.4);
}
.lumi-check .box.on { background: var(--lumi-accent); border-color: var(--lumi-accent); box-shadow: 0 0 7px color-mix(in srgb, var(--lumi-accent) 55%, transparent); }
.lumi-check .box.on::after { content: ''; width: 8px; height: 4.5px; border-left: 2.2px solid #042018; border-bottom: 2.2px solid #042018; transform: rotate(-45deg) translateY(-1px); }
.lumi-check .txt { font-size: 12px; color: var(--lumi-text); line-height: 1.2; white-space: normal; }
/* your Lumiora volume bar: rounded bar, accent fill, bold % centered.
   higher specificity than .tk-slider.lux so the accent var actually wins */
.tk-slider.lux.lumi-slider { padding: 0; }
.tk-slider.lux.lumi-slider .track {
  height: 100%; border-radius: 7px;
  background: var(--lumi-track); border: 1px solid var(--lumi-border);
  box-shadow: inset 0 1.5px 3px rgba(0,0,0,.35);
}
.tk-slider.lux.lumi-slider .fill {
  top: 1px; bottom: 1px; left: 1px; right: auto;
  background: var(--lumi-fill, var(--lumi-accent)); border-radius: 6px;
  box-shadow: 0 0 10px color-mix(in srgb, var(--lumi-fill, var(--lumi-accent)) 40%, transparent);
}
.tk-slider.lux.lumi-slider .knob { display: none; }
.lumi-slider .lumi-val {
  position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); z-index: 2;
  font-size: 11px; font-weight: 800; color: var(--lumi-fillink);
  letter-spacing: .02em; text-shadow: 0 1px 2px rgba(0,0,0,.5); pointer-events: none;
  white-space: nowrap;
}
.lumi-dropdown {
  width: 100%; height: 100%; border-radius: var(--lumi-radius, 9px);
  background: var(--lumi-surface2); border: 1px solid var(--lumi-border);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.05);
  display: flex; align-items: center; padding: 0 12px; gap: 6px;
}
.lumi-dropdown .dd-txt { flex: 1; font-size: 12px; color: var(--lumi-text); overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.lumi-dropdown .car {
  width: 7px; height: 7px; border-right: 1.8px solid var(--lumi-sub); border-bottom: 1.8px solid var(--lumi-sub);
  transform: rotate(45deg) translateY(-2px); flex: none;
}
.lumi-input {
  width: 100%; height: 100%; border-radius: var(--lumi-radius, 9px);
  background: #161b22; border: 1px solid var(--lumi-border);
  box-shadow: inset 0 2px 3px rgba(0,0,0,.35);
  display: flex; align-items: center; padding: 0 12px;
}
.lumi-input .ph { font-size: 12px; color: #5d6b81; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.lumi-btn {
  width: 100%; height: 100%; border-radius: var(--lumi-radius, 10px);
  display: flex; align-items: center; justify-content: center;
  font-size: 12.5px; font-weight: 700; overflow: hidden; white-space: nowrap;
  padding: 0 10px; text-shadow: 0 1px 1px rgba(0,0,0,.25); color: var(--lumi-fillink);
}
.lumi-btn.primary {
  background: linear-gradient(180deg, color-mix(in srgb, var(--lumi-accent) 88%, #ffffff), var(--lumi-accent));
  box-shadow: 0 2px 12px color-mix(in srgb, var(--lumi-accent) 40%, transparent), inset 0 1px 0 rgba(255,255,255,.2);
}
.lumi-btn.pill {
  background: var(--lumi-surface); border: 1px solid var(--lumi-border); border-radius: var(--lumi-radius, 99px); font-weight: 600;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.05);
}
.lumi-prog { width: 100%; height: 100%; display: flex; align-items: center; }
.lumi-prog .tr {
  width: 100%; height: 100%; max-height: 8px; border-radius: var(--lumi-radius, 99px);
  background: var(--lumi-track); border: 1px solid var(--lumi-border);
  box-shadow: inset 0 1.5px 3px rgba(0,0,0,.45); overflow: hidden;
}
.lumi-prog .fl { height: 100%; background: var(--lumi-fill, var(--lumi-accent)); border-radius: 99px; box-shadow: 0 0 8px color-mix(in srgb, var(--lumi-fill, var(--lumi-accent)) 50%, transparent); }
.lumi-card { width: 100%; height: 100%; border-radius: var(--lumi-radius, 14px); border: 1px solid var(--lumi-border); background: var(--lumi-surface); box-shadow: inset 0 1px 0 rgba(255,255,255,.05), 0 8px 24px rgba(0,0,0,.25); }
.lumi-card.grad {
  /* native GradientCard defaults to the theme surface when no fill is set —
     the preview must match (a hardcoded darker tone read as "wrong color") */
  background: var(--lumi-surface);
  border: none; position: relative;
  box-shadow: 0 0 18px color-mix(in srgb, var(--lumi-accent) 22%, transparent), inset 0 1px 0 rgba(255,255,255,.05);
}
/* the animated gradient edge — same as the native renderer: a static
   teal→purple ring is always lit, and a bright traveling light sweeps
   around it (the library's static_ring + gradient_ring streak). */
@property --lumi-a { syntax: '<angle>'; inherits: false; initial-value: 0deg; }
.lumi-card.grad::before {
  content: ''; position: absolute; inset: 0; border-radius: var(--lumi-radius, 14px); padding: 2px;
  background:
    linear-gradient(135deg, var(--lumi-accent), color-mix(in srgb, var(--lumi-accent) 55%, #38bdf8), #a78bfa),
    conic-gradient(from var(--lumi-a),
      rgba(255,255,255,0) 0deg,
      rgba(255,255,255,.9) 20deg,
      rgba(255,255,255,0) 42deg);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude;
  opacity: .9;
  animation: lumi-spin 5s linear infinite;
}
@keyframes lumi-spin { to { --lumi-a: 360deg; } }

/* ============================ custom widget chip (canvas) ============================ */
.tk-custom {
  width: 100%; height: 100%; display: flex; flex-direction: column;
  background: linear-gradient(165deg, #1a2029, #141920);
  border: 1.5px dashed rgba(52, 211, 153, .55); border-radius: 6px;
  padding: 4px 7px; overflow: hidden; min-width: 0;
}
.tk-custom .cc-head { display: flex; align-items: center; gap: 6px; min-width: 0; }
.tk-custom .cc-chip {
  width: 9px; height: 9px; flex: none; border-radius: 3px;
  background: linear-gradient(135deg, var(--accent), var(--accent-dim));
  box-shadow: 0 0 6px rgba(52, 211, 153, .6);
}
.tk-custom .cc-name {
  font-size: 10px; font-weight: 800; color: var(--accent);
  overflow: hidden; white-space: nowrap; text-overflow: ellipsis;
}
.tk-custom .cc-code {
  margin-top: 3px; font-family: var(--font-mono); font-size: 9px;
  color: #5d6b81; overflow: hidden; white-space: pre;
  text-overflow: ellipsis; line-height: 1.5;
}

/* ============================ lumiora effects: window glow + particles ============================ */
.stage-win.lfx-glow .design-win {
  box-shadow:
    0 0 46px 6px color-mix(in srgb, var(--win-glow, #5b8cff) 30%, transparent),
    0 0 0 1px rgba(0,0,0,.4),
    0 26px 70px rgba(0,0,0,.6);
}
/* Layer 1 — the particle field: a transparent effect layer that belongs to
   the window background only. It fills the window and stays strictly
   inside the rounded window, BEHIND the background image and every widget
   on it (the image sits at z2, the login UI at z4). Normal alpha
   compositing (like the native renderer) — no blend modes, no transparent
   gaps that could reveal anything behind. */
.lfx-particles {
  position: absolute; inset: 0; pointer-events: none; z-index: 1;
  overflow: hidden;
}
/* layer fade helpers — the field dissolves in on appear, out on disable,
   and cross-fades between modes; the window vignette leaves with it */
.fx-content { width: 100%; height: 100%; }
.fx-content.fx-in { animation: lfx-in .55s ease-out both; }
.lfx-particles.fx-ghost { animation: lfx-out .5s ease forwards; }
.lfx-particles.fx-off { opacity: 0 !important; transition: opacity .45s ease; }
.lfx-vig.fx-off { opacity: 0 !important; transition: opacity .45s ease; }
@keyframes lfx-in {
  from { opacity: 0; transform: scale(1.02); }
  to { opacity: 1; transform: none; }
}
@keyframes lfx-out {
  from { opacity: var(--lfx-go, .6); }
  to { opacity: 0; }
}
/* Layer 3 — subtle edge overlay (the native vignette rim) */
.lfx-vig {
  position: absolute; inset: 0; pointer-events: none; z-index: 3;
  box-shadow:
    inset 0 0 20px 2px rgba(5, 6, 8, .30),
    inset 0 0 54px 10px rgba(5, 6, 8, .20),
    inset 0 0 110px 26px rgba(5, 6, 8, .15);
}
/* when particles are on the window is in "final look" mode — the snap grid
   (a design aid, not part of the render) must not show through */
.stage-win.lfx-particled .frame-grid-overlay { display: none; }
/* hexagon mode — ported from the library's _draw_forming_hexes: a full
   pointy-top honeycomb grid covering the window (brass outlines, faint
   fill). Every cell runs the same fade-out -> cleared hold -> fade-in
   envelope on its loop, and each cell's negative delay is offset by its
   row from the top edge of the window — so a soft clearing wave starts at
   the top and travels all the way down, then the hexagons reform the same
   top-to-bottom way. ~5% of cells are "hot": brighter + glowing. */
.lfx-particles.mode-hexagon {
  --hx1: #d4a86a;  /* the reference's warm brass */
  --hx2: #c49c54;
  --hx3: #eccf95;
}
.lfx-particles svg.hx-lattice {
  position: absolute; inset: 0; width: 100%; height: 100%;
}
.lfx-particles .hx {
  fill: var(--hx1); fill-opacity: .08;
  stroke: var(--hx1); stroke-opacity: .85; stroke-width: 1;
  vector-effect: non-scaling-stroke;
  animation-name: lfx-hexlife;
  animation-iteration-count: infinite;
  animation-timing-function: ease-in-out;
}
.lfx-particles .hx.hot {
  fill-opacity: .16; stroke-opacity: 1; stroke-width: 1.4;
  filter: drop-shadow(0 0 4px rgba(212, 168, 106, .6));
}
@keyframes lfx-hexlife {
  /* one cell's envelope: fully lit, soft fade out, a cleared pause, soft
     fade back in, then a calm, fully-lit rest. Cells are staggered along
     the top-left -> bottom-right diagonal (per-cell negative delays set by
     the generators) so the fade-out and the fade-in each sweep from corner
     to corner instead of blinking per cell. */
  0%   { opacity: 1; }
  26%  { opacity: 1; }
  36%  { opacity: .3; }
  44%  { opacity: .02; }    /* gone */
  60%  { opacity: .02; }    /* cleared hold */
  70%  { opacity: .35; }
  78%  { opacity: 1; }
  100% { opacity: 1; }      /* rest fully lit */
}
/* particles (dust) mode — ported from the library's _draw_dust: two depth
   layers of lavender / ivory / pale-blue motes. Each mote is an outer
   span (its base brightness, one of two depth layers) around an inner
   dot that glows and drifts upward while popping in and out. */
.lfx-particles.mode-particles {
  --hx1: #d8d4e4;  /* lavender */
  --hx2: #e4dcc8;  /* ivory */
  --hx3: #c8d8e4;  /* pale blue */
  background:
    radial-gradient(58% 44% at 26% 28%, rgba(216, 212, 228, .05), transparent 70%),
    radial-gradient(55% 42% at 78% 70%, rgba(200, 216, 228, .045), transparent 70%);
}
.lfx-particles .mx {
  position: absolute;
  animation-name: lfx-motedrift;
  animation-iteration-count: infinite;
  animation-timing-function: ease-in-out;
}
.lfx-particles .mx i {
  position: absolute; inset: 0; border-radius: 50%;
  background: var(--hc, var(--hx2));
  box-shadow: 0 0 5px 1px color-mix(in srgb, var(--hc, var(--hx2)) 55%, transparent);
  animation-name: lfx-motepulse;
  animation-iteration-count: infinite;
  animation-timing-function: ease-in-out;
}
.lfx-particles .mx.far i {
  box-shadow: 0 0 3px 1px color-mix(in srgb, var(--hc, var(--hx2)) 40%, transparent);
}
@keyframes lfx-motedrift {
  /* gentle upward drift with a sway — quiet at both ends, so the wrap
     reads as a mote dissolving out and a fresh one popping in below */
  0%   { transform: translate3d(0px, 30px, 0); }
  22%  { transform: translate3d(7px, 6px, 0); }
  46%  { transform: translate3d(-8px, -18px, 0); }
  70%  { transform: translate3d(5px, -44px, 0); }
  100% { transform: translate3d(-2px, -86px, 0); }
}
@keyframes lfx-motepulse {
  0%   { opacity: 0; }
  11%  { opacity: .9; }
  32%  { opacity: .55; }
  55%  { opacity: .8; }
  78%  { opacity: .3; }
  94%  { opacity: .06; }
  100% { opacity: 0; }
}

/* lumiora widget previews that run the same animated fx as the window
   background: Hexagon field / Particle field layers + Particle card */
.lumi-fxbox {
  position: absolute; inset: 0; border-radius: 12px; overflow: hidden;
}
.lumi-fxbox.carded {
  border: 1px solid var(--lumi-border, #2e313a);
  border-radius: var(--lumi-radius, 14px);
  /* native Card(fill=None, particles=True) paints the theme surface under
     the field — preview must agree */
  background: var(--lumi-surface, #16191f);
  mix-blend-mode: normal;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, .04);
}
.lumi-fxbox.carded .hx { stroke-opacity: .5; }
.lumi-fxbox .mx i { box-shadow: none; }
.lumi-img {
  position: absolute; inset: 0; overflow: hidden;
  display: flex; align-items: center; justify-content: center;
  border: 1px solid var(--lumi-border, #2e313a);
  border-radius: var(--lumi-radius, 10px);
  background: linear-gradient(135deg, #1a2030, #131820);
  color: var(--lumi-sub, #7c8698); font-size: 9.5px; text-align: center;
  padding: 6px; line-height: 1.5;
}
.lumi-img img { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
.lumi-img.empty { border-style: dashed; }
.lumi-txt {
  position: absolute; inset: 0; display: flex; align-items: center;
  justify-content: flex-start; text-align: left; color: var(--lumi-text, #eef2f8);
  overflow: hidden; white-space: nowrap; text-overflow: ellipsis;
}
/* neon gradient edge on buttons — the traveling light, ported look */
.lumi-btn.neon { position: relative; }
.lumi-btn.neon::before {
  content: ''; position: absolute; inset: -1px;
  border-radius: inherit;
  padding: 1.6px;
  background:
    conic-gradient(from 180deg, #34d399, #38bdf8, #a78bfa, #34d399),
    conic-gradient(from var(--lumi-a),
      rgba(255,255,255,0) 0deg,
      rgba(255,255,255,.95) 24deg,
      rgba(255,255,255,0) 50deg);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  mask-composite: exclude;
  animation: lumi-spin 4.5s linear infinite;
  pointer-events: none;
}

/* ============================ new lumiora previews ============================ */
.lumi-btn.ghost {
  background: transparent; color: var(--lumi-text);
  border: 1px solid transparent; box-shadow: none;
}
.tk-slider.lumi-thin { padding: 0; gap: 0; }
.lumi-thin .track {
  position: relative; height: 5px; border-radius: 99px;
  background: var(--lumi-track); border: 1px solid var(--lumi-border);
}
.lumi-thin .fill {
  position: absolute; left: 0; top: 0; bottom: 0;
  background: var(--lumi-accent); border-radius: 99px;
}
.lumi-thin .knob {
  position: absolute; top: 50%; width: 15px; height: 15px;
  background: #e9eef5; border-radius: 50%; transform: translate(-50%, -50%);
  border: 2px solid var(--lumi-accent); box-shadow: 0 1px 4px rgba(0,0,0,.45);
}
.lumi-dropdown.combo { position: relative; }
.lumi-dropdown.combo .combo-head {
  display: flex; align-items: center; gap: 6px; min-width: 0; flex: 1;
}
.lumi-dropdown.combo .combo-head .edit {
  width: 4px; height: 4px; flex: none; border-bottom: 1.5px solid var(--lumi-sub);
}
.lumi-dropdown.combo .combo-arrow {
  font-size: 7px; color: var(--lumi-sub); flex: none;
}
.lumi-frame {
  width: 100%; height: 100%; background: var(--lumi-surface);
  display: flex; flex-direction: column; gap: 8px; padding: 12px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.04); overflow: hidden;
}
.lumi-frame .lumi-frame-mid { flex: 1; border-radius: 6px; background: var(--lumi-surface2); }
.lumi-hexfield {
  width: 100%; height: 100%; border-radius: 14px;
  background:
    radial-gradient(circle at 26% 32%, rgba(91,140,255,.28) 0, transparent 30%),
    radial-gradient(circle at 72% 26%, rgba(167,139,250,.26) 0, transparent 28%),
    radial-gradient(circle at 66% 76%, rgba(34,211,238,.24) 0, transparent 30%),
    #10141c;
  position: relative; overflow: hidden;
}
.lumi-hexfield::before {
  content: ''; position: absolute; inset: 0;
  background-image:
    linear-gradient(30deg, rgba(120,150,255,.34) 12%, transparent 12.5%, transparent 87%, rgba(120,150,255,.34) 87.5%),
    linear-gradient(150deg, rgba(120,150,255,.34) 12%, transparent 12.5%, transparent 87%, rgba(120,150,255,.34) 87.5%),
    linear-gradient(30deg, rgba(120,150,255,.34) 12%, transparent 12.5%, transparent 87%, rgba(120,150,255,.34) 87.5%),
    linear-gradient(150deg, rgba(120,150,255,.34) 12%, transparent 12.5%, transparent 87%, rgba(120,150,255,.34) 87.5%);
  background-size: 44px 76px; background-position: 0 0, 0 0, 22px 38px, 22px 38px;
  animation: lfx-hex 12s linear infinite;
  opacity: .8;
}
.lumi-hexfield.carded {
  border: 1px solid var(--lumi-border);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.05), 0 8px 24px rgba(0,0,0,.3);
}
@keyframes lfx-hex {
  from { background-position: 0 0, 0 0, 22px 38px, 22px 38px; }
  to   { background-position: 44px 76px, 44px 76px, 66px 114px, 66px 114px; }
}
.lumi-dyn {
  width: 100%; height: 100%; border-radius: var(--lumi-radius, 20px);
  background: var(--lumi-surface2); border: 1px solid var(--lumi-border);
  display: flex; align-items: center; padding: 4px; gap: 4px;
}
.lumi-dyn span {
  flex: 1; text-align: center; font-size: 11.5px; font-weight: 600; color: var(--lumi-sub);
  padding: 5px 0; border-radius: calc(var(--lumi-radius, 20px) - 5px);
}
.lumi-dyn span.act {
  /* the library's white-pill-on-dark-track capsule */
  background: #f2f4fa; color: #10131c;
  box-shadow: 0 1px 6px rgba(0, 0, 0, .4);
}
.lumi-log {
  width: 100%; height: 100%; border-radius: var(--lumi-radius, 10px);
  background: #0d1016; border: 1px solid var(--lumi-border);
  padding: 6px 9px; display: flex; flex-direction: column; gap: 4px; overflow: hidden;
  font-family: var(--font-mono); font-size: 9.5px; color: #a7b0c0;
}
.lumi-log .lrow { display: flex; align-items: center; gap: 6px; white-space: nowrap; overflow: hidden; }
.lumi-log .lrow i { width: 6px; height: 6px; flex: none; border-radius: 50%; }
.lumi-log .lrow i.ok { background: #3dd68c; box-shadow: 0 0 5px #3dd68c; }
.lumi-log .lrow i.info { background: #5b8cff; box-shadow: 0 0 5px #5b8cff; }
.lumi-log .lrow i.warn { background: #f5b942; box-shadow: 0 0 5px #f5b942; }
/* user-styled corner radius applies to every lumi preview surface */
.lumi-btn, .lumi-toggle::before, .lumi-check .box, .lumi-dropdown,
.lumi-prog .tr, .lumi-card, .lumi-frame, .lumi-dyn {
  border-radius: var(--lumi-radius, 10px);
}

/* separators / small helpers */
.hint-note { font-size: 10.5px; color: var(--faint); line-height: 1.65; margin-top: 2px; }

"""

# one page per layout window — served at /win/0, /win/1, ...
WINDOW_PAGES = [
"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Calculator — lumi-calc</title>
<link rel="stylesheet" href="/style.css" />
<style>

/* the real OS window has no page chrome — kill any scrollbars and make
   the design surface fill the window EXACTLY (the design IS the window) */
html, body { overflow: hidden !important; }
.desktop-stage {
  padding: 0 !important;
  display: block !important;
  min-height: 100vh;
  overflow: hidden;
  background: #0a0d12;  /* overridden per page with the window's own bg */
}
.desk-win {
  position: fixed; inset: 0; width: 100vw !important; height: 100vh !important;
  box-sizing: border-box;
}
.desk-win .window-chrome { border-radius: 0; }
.desk-win .design-win {
  /* fill the window 1:1 — the width/height inline on the node are
     overridden, so the rendered card is always exactly the design size */
  width: 100% !important;
  height: 100% !important;
  box-sizing: border-box;
  box-shadow: none;
  border-radius: 0 0 10px 10px;
}
/* glowing designs: the native host gives the window real per-pixel
   transparency, so the page carries a transparent margin around the card
   and the REAL outer glow (exactly the canvas glow) renders outside it.
   The per-page glow overrides below size the card and paint that glow. */
/* a window with a title bar in the design keeps it: the surface is the
   remaining 32px below the bar */
.desk-win .window-chrome + .design-win { height: calc(100% - 32px) !important; }
/* the whole title bar drags the window; controls stay clickable */
.win-chrome { -webkit-app-region: drag; }
.win-chrome .win-controls,
.win-chrome .wc,
.win-chrome .dots-live .dot { -webkit-app-region: no-drag; }
/* live traffic-light dots in the chrome bar — red closes, yellow
   minimizes, green maximizes (same look as the canvas dots; the glyph
   and a brighten appear on hover) */
.desk-win .window-chrome .dots-live { display: flex; gap: 5px; flex: none; }
.desk-win .window-chrome .dots-live .dot {
  width: 10px; height: 10px; padding: 0; margin: 0; border: 0;
  border-radius: 50%; box-sizing: border-box; outline: none;
  display: grid; place-items: center; line-height: 0; cursor: pointer;
  transition: filter .1s ease;
}
.desk-win .window-chrome .dots-live .dot svg {
  width: 7px; height: 7px; color: rgba(8, 10, 16, .8); opacity: 0;
  transition: opacity .1s ease;
}
.desk-win .window-chrome .dots-live .dot:hover svg { opacity: 1; }
.desk-win .window-chrome .dots-live .dot:hover { filter: brightness(1.14); }
.desk-win .window-chrome .dots-live .dot-close { background: #ff5f57; }
.desk-win .window-chrome .dots-live .dot-min { background: #febc2e; }
.desk-win .window-chrome .dots-live .dot-max { background: #28c840; }
.win-controls { flex: none; display: flex; align-items: stretch; height: 100%; }
.wc {
  width: 44px; height: 100%; padding: 0; margin: 0; border: 0;
  background: transparent; color: #98a2b8; cursor: default;
  display: grid; place-items: center; outline: none;
  font: inherit;
}
.wc:hover { background: rgba(255,255,255,.09); color: #f2f4fa; }
.wc-close:hover { background: #e81123; color: #ffffff; }
/* frameless designs keep no chrome bar — a small control cluster fades in
   at the top-right on hover, so the window still has working controls
   while looking exactly like the design when idle */
.desk-float-controls {
  position: absolute; top: 10px; right: 10px; z-index: 90;
  display: flex; gap: 2px; padding: 2px;
  border-radius: 10px;
  background: rgba(15,18,26,.78);
  border: 1px solid rgba(255,255,255,.08);
  box-shadow: 0 6px 18px rgba(0,0,0,.5);
  opacity: 0; transition: opacity .15s ease;
  pointer-events: none;
}
.desk-win:hover .desk-float-controls { opacity: 1; pointer-events: auto; }
/* widgets with an action or custom click code read as clickable */
.webapp-stage .wnode[data-lumi-open], .webapp-stage .wnode[data-lumi-fn] { cursor: pointer; }
.desk-float-controls .wc { width: 30px; height: 26px; border-radius: 7px; }
.desk-float-controls .wc:hover { background: rgba(255,255,255,.14); }
.desktop-stage.is-browser .win-controls,
.desktop-stage.is-browser .desk-float-controls { display: none; }
/* close: the window content melts away (fade + gentle shrink) just before
   the OS window actually closes — clean, never a hard pop */
.lumi-closing .desk-win {
  animation: lumi-out .2s cubic-bezier(.5, .05, .6, .4) forwards;
}
@keyframes lumi-out {
  to { opacity: 0; transform: scale(.93) translateY(18px); }
}
/* minimize needs no page animation — the native host slides the whole OS
   window straight down out of view into the taskbar (see _cmd_minimize),
   then really minimizes; restoring pops it back in normally. */

</style>
<style>

.desk-win.desk-glow {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.desk-win.desk-glow .design-win {
  width: 340px !important;
  height: 480px !important;
  box-shadow:
    0 0 46px 6px color-mix(in srgb, var(--win-glow, #5b8cff) 30%, transparent),
    0 0 0 1px rgba(0,0,0,.4),
    0 26px 70px rgba(0,0,0,.6);
}

</style>

</head>
<body class="webapp-stage desktop-stage" style="background:transparent">
<div class="stage-win lfx-glow desk-win desk-glow" style="width:340px;height:480px"><span class="desk-float-controls"><button class="wc wc-min" title="Minimize" aria-label="Minimize"><svg width="10" height="10" viewBox="0 0 10 10"><path d="M1 5h8" stroke="currentColor" stroke-width="1.2">
</path>
</svg>
</button><button class="wc wc-max" title="Maximize" aria-label="Maximize"><svg width="10" height="10" viewBox="0 0 10 10"><rect x="1" y="1" width="8" height="8" fill="none" stroke="currentColor" stroke-width="1.2">
</rect>
</svg>
</button><button class="wc wc-close" title="Close" aria-label="Close"><svg width="10" height="10" viewBox="0 0 10 10"><path d="M1.5 1.5l7 7M8.5 1.5l-7 7" stroke="currentColor" stroke-width="1.2">
</path>
</svg>
</button>
</span><div class="design-win" style="width:340px;height:480px;background:#0c0e14;border-radius:20px;--win-glow:#34d399"><div class="wnode" data-name="CALCULATOR" style="left:28px;top:12px;width:284px;height:14px;z-index:1"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:8px;--lumi-fill:#34d399"><div class="lumi-txt" style="font-family:Helvetica, sans-serif;font-size:9px;font-weight:700;letter-spacing:4px;color:#5b6478">CALCULATOR</div>
</div>
</div><div class="wnode" data-name="display" style="left:28px;top:30px;width:284px;height:76px;z-index:1"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:8px;--lumi-fill:#34d399"><div class="lumi-txt" style="font-family:Helvetica, sans-serif;font-size:40px;font-weight:700;color:#f2f6fc;text-align:center;justify-content:center">0</div>
</div>
</div><div class="wnode" data-name="C" style="left:28px;top:116px;width:64px;height:60px;z-index:1" data-lumi-fn="wmtnr9l281goaxl"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:16px;--lumi-fill:#221818"><div class="lumi-btn pill" style="font-family:Helvetica, sans-serif;font-size:15px;font-weight:700;color:#ff8f8f;background:#221818">C</div>
</div>
</div><div class="wnode" data-name="DEL" style="left:100px;top:116px;width:64px;height:60px;z-index:1" data-lumi-fn="wmtnr9l281hojfo"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:16px;--lumi-fill:#221818"><div class="lumi-btn pill" style="font-family:Helvetica, sans-serif;font-size:15px;font-weight:700;color:#ff8f8f;background:#221818">DEL</div>
</div>
</div><div class="wnode" data-name="%" style="left:172px;top:116px;width:64px;height:60px;z-index:1" data-lumi-fn="wmtnr9l281izj75"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:16px;--lumi-fill:#1a2130"><div class="lumi-btn pill" style="font-family:Helvetica, sans-serif;font-size:18px;font-weight:700;color:#67e8f9;background:#1a2130">%</div>
</div>
</div><div class="wnode" data-name="÷" style="left:244px;top:116px;width:64px;height:60px;z-index:1" data-lumi-fn="wmtnr9l281j9cio"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:16px;--lumi-fill:#1a2130"><div class="lumi-btn pill" style="font-family:Helvetica, sans-serif;font-size:18px;font-weight:700;color:#67e8f9;background:#1a2130">÷</div>
</div>
</div><div class="wnode" data-name="7" style="left:28px;top:184px;width:64px;height:60px;z-index:1" data-lumi-fn="wmtnr9l281k46jv"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:16px;--lumi-fill:#161a24"><div class="lumi-btn pill" style="font-family:Helvetica, sans-serif;font-size:17px;font-weight:700;color:#eef2f8;background:#161a24">7</div>
</div>
</div><div class="wnode" data-name="8" style="left:100px;top:184px;width:64px;height:60px;z-index:1" data-lumi-fn="wmtnr9l281ltfyc"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:16px;--lumi-fill:#161a24"><div class="lumi-btn pill" style="font-family:Helvetica, sans-serif;font-size:17px;font-weight:700;color:#eef2f8;background:#161a24">8</div>
</div>
</div><div class="wnode" data-name="9" style="left:172px;top:184px;width:64px;height:60px;z-index:1" data-lumi-fn="wmtnr9l281m33po"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:16px;--lumi-fill:#161a24"><div class="lumi-btn pill" style="font-family:Helvetica, sans-serif;font-size:17px;font-weight:700;color:#eef2f8;background:#161a24">9</div>
</div>
</div><div class="wnode" data-name="×" style="left:244px;top:184px;width:64px;height:60px;z-index:1" data-lumi-fn="wmtnr9l281nro4g"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:16px;--lumi-fill:#1a2130"><div class="lumi-btn pill" style="font-family:Helvetica, sans-serif;font-size:18px;font-weight:700;color:#67e8f9;background:#1a2130">×</div>
</div>
</div><div class="wnode" data-name="4" style="left:28px;top:252px;width:64px;height:60px;z-index:1" data-lumi-fn="wmtnr9l281orm5t"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:16px;--lumi-fill:#161a24"><div class="lumi-btn pill" style="font-family:Helvetica, sans-serif;font-size:17px;font-weight:700;color:#eef2f8;background:#161a24">4</div>
</div>
</div><div class="wnode" data-name="5" style="left:100px;top:252px;width:64px;height:60px;z-index:1" data-lumi-fn="wmtnr9l281p87x3"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:16px;--lumi-fill:#161a24"><div class="lumi-btn pill" style="font-family:Helvetica, sans-serif;font-size:17px;font-weight:700;color:#eef2f8;background:#161a24">5</div>
</div>
</div><div class="wnode" data-name="6" style="left:172px;top:252px;width:64px;height:60px;z-index:1" data-lumi-fn="wmtnr9l281q6806"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:16px;--lumi-fill:#161a24"><div class="lumi-btn pill" style="font-family:Helvetica, sans-serif;font-size:17px;font-weight:700;color:#eef2f8;background:#161a24">6</div>
</div>
</div><div class="wnode" data-name="−" style="left:244px;top:252px;width:64px;height:60px;z-index:1" data-lumi-fn="wmtnr9l281rllvi"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:16px;--lumi-fill:#1a2130"><div class="lumi-btn pill" style="font-family:Helvetica, sans-serif;font-size:18px;font-weight:700;color:#67e8f9;background:#1a2130">−</div>
</div>
</div><div class="wnode" data-name="1" style="left:28px;top:320px;width:64px;height:60px;z-index:1" data-lumi-fn="wmtnr9l281sl4xm"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:16px;--lumi-fill:#161a24"><div class="lumi-btn pill" style="font-family:Helvetica, sans-serif;font-size:17px;font-weight:700;color:#eef2f8;background:#161a24">1</div>
</div>
</div><div class="wnode" data-name="2" style="left:100px;top:320px;width:64px;height:60px;z-index:1" data-lumi-fn="wmtnr9l281tksv6"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:16px;--lumi-fill:#161a24"><div class="lumi-btn pill" style="font-family:Helvetica, sans-serif;font-size:17px;font-weight:700;color:#eef2f8;background:#161a24">2</div>
</div>
</div><div class="wnode" data-name="3" style="left:172px;top:320px;width:64px;height:60px;z-index:1" data-lumi-fn="wmtnr9l281usc9t"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:16px;--lumi-fill:#161a24"><div class="lumi-btn pill" style="font-family:Helvetica, sans-serif;font-size:17px;font-weight:700;color:#eef2f8;background:#161a24">3</div>
</div>
</div><div class="wnode" data-name="+" style="left:244px;top:320px;width:64px;height:60px;z-index:1" data-lumi-fn="wmtnr9l281vy6ib"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:16px;--lumi-fill:#1a2130"><div class="lumi-btn pill" style="font-family:Helvetica, sans-serif;font-size:18px;font-weight:700;color:#67e8f9;background:#1a2130">+</div>
</div>
</div><div class="wnode" data-name="0" style="left:28px;top:388px;width:136px;height:60px;z-index:1" data-lumi-fn="wmtnr9l281woh84"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:16px;--lumi-fill:#161a24"><div class="lumi-btn pill" style="font-family:Helvetica, sans-serif;font-size:17px;font-weight:700;color:#eef2f8;background:#161a24">0</div>
</div>
</div><div class="wnode" data-name="." style="left:172px;top:388px;width:64px;height:60px;z-index:1" data-lumi-fn="wmtnr9l281xzu6u"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:16px;--lumi-fill:#161a24"><div class="lumi-btn pill" style="font-family:Helvetica, sans-serif;font-size:17px;font-weight:700;color:#eef2f8;background:#161a24">.</div>
</div>
</div><div class="wnode" data-name="=" style="left:244px;top:388px;width:64px;height:60px;z-index:1" data-lumi-fn="wmtnr9l281yye5x"><div class="lumi-pv t-dark" style="--lumi-accent:#34d399;--lumi-radius:16px;--lumi-fill:#34d399"><div class="lumi-btn primary" style="font-family:Helvetica, sans-serif;font-size:20px;font-weight:700;color:#05261b;background:#34d399">=</div>
</div>
</div>
</div>
</div>
<script>

(function () {
  'use strict';
  // gooey toggles
  document.querySelectorAll('.lumi-goo').forEach(function (el) {
    el.addEventListener('click', function () { el.classList.toggle('on'); });
  });
  // checkboxes
  document.querySelectorAll('.lumi-check').forEach(function (el) {
    el.addEventListener('click', function () {
      var box = el.querySelector('.box');
      if (box) box.classList.toggle('on');
    });
  });
  // segmented (dynamic) toggles
  document.querySelectorAll('.lumi-dyn').forEach(function (el) {
    var opts = [].slice.call(el.querySelectorAll('span'));
    opts.forEach(function (o) {
      o.addEventListener('click', function () {
        opts.forEach(function (x) { x.classList.remove('act'); });
        o.classList.add('act');
      });
    });
  });
})();


(function () {
  'use strict';
  function wire() {
    var api = null;
    try { api = window.pywebview && window.pywebview.api; } catch (e) { api = null; }
    if (!api) return;
    document.body.classList.add('is-desktop');
    function fire(name) {
      return function () { try { api[name](); } catch (e) {} };
    }
    function onAll(sel, fn) {
      Array.prototype.forEach.call(document.querySelectorAll(sel), function (el) {
        el.addEventListener('click', fn);
      });
    }
    // minimize slides the window out (host-side animation)
    // close first plays the fade-out animation, then really closes
    function requestClose() {
      if (document.body.classList.contains('lumi-closing')) return;
      document.body.classList.add('lumi-closing');
      setTimeout(function () { try { api.close(); } catch (e) {} }, 210);
    }
    onAll('.wc-min, .dot-min', fire('minimize'));
    onAll('.wc-max, .dot-max', fire('toggle_maximize'));
    onAll('.wc-close, .dot-close', requestClose);
    // widgets with an "open window" action: clicking the widget opens that
    // window (the host keeps it closed at launch until this click)
    document.addEventListener('click', function (e) {
      var t = e.target;
      var el = (t && t.closest) ? t.closest('[data-lumi-open]') : null;
      if (!el) return;
      if (t.closest('.wc') || t.closest('.dot')) return;
      var i = Number(el.getAttribute('data-lumi-open'));
      if (!isNaN(i)) { try { api.open_win(i); } catch (err) {} }
    }, true);
  }
  window.addEventListener('pywebviewready', function () {
    document.body.classList.remove('is-browser');
    wire();
  });
  wire();
  setTimeout(function () {
    if (!document.body.classList.contains('is-desktop')) {
      document.body.classList.add('is-browser');
    }
  }, 1500);
})();

</script>
<script>
(function(){
if(window.__lumiReady)return;
window.__lumiReady=true;
var H=window.__lumiH=window.__lumiH||{};
window.__lumiM=window.__lumiM||{};
function elOf(stage,name){var list=stage?stage.querySelectorAll('.wnode[data-name]'):document.querySelectorAll('.wnode[data-name]');for(var i=0;i<list.length;i++){if(list[i].getAttribute('data-name')===name){var ts=list[i].querySelectorAll('.lumi-txt');for(var j=0;j<ts.length;j++){if(!ts[j].closest('.wnode .wnode'))return ts[j];}return list[i];}}return null;}
function runExpr(x){if(typeof x!=='string'||!/^[0-9+\\-*/.() ]*$/.test(x)){throw new Error('unsafe expression');}return Function('return('+x+')')();}
document.addEventListener('click',function(e){var t=e.target;var el0=(t&&t.closest)?t.closest('[data-lumi-fn]'):null;if(!el0)return;if(t.closest&&(t.closest('.wc')||t.closest('.dot')))return;var id=el0.getAttribute('data-lumi-fn');var fn=H[id];if(!fn)return;var stage=el0.closest?el0.closest('.stage-win'):null;var api=(window.pywebview&&window.pywebview.api)||{};var tools={el:function(name){return elOf(stage||document.body,name)},run:runExpr,mem:window.__lumiM};try{fn.call(el0,e,api,tools);}catch(err){}
},true);
H['wmtnr9l281goaxl']=function(ev,api,tools){var el=tools.el,run=tools.run,mem=tools.mem;
var c=mem,d=el('display');c.p='0';c.q='0';c.dn=0;d.textContent='0';
};
H['wmtnr9l281hojfo']=function(ev,api,tools){var el=tools.el,run=tools.run,mem=tools.mem;
var c=mem,d=el('display');c.q=c.q||'0';c.p=c.p||'0';var e=c.q.slice(-1);if('+-*/'.indexOf(e)>=0){c.q=c.q.slice(0,-1);c.p=c.p.slice(0,-3)}else{c.q=c.q.slice(0,-1);c.p=c.p.slice(0,-1)}if(!c.p){c.p='0';c.q='0'}d.textContent=c.p;
};
H['wmtnr9l281izj75']=function(ev,api,tools){var el=tools.el,run=tools.run,mem=tools.mem;
var c=mem,d=el('display');c.q=c.q||'0';var q=c.q;var e=q.slice(-1);if('+-*/'.indexOf(e)>=0){q=q.slice(0,-1)}var i=Math.max(q.lastIndexOf('+'),q.lastIndexOf('-'),q.lastIndexOf('*'),q.lastIndexOf('/'));var b=q.slice(i+1);if(b!==''){q=q.slice(0,i+1)+String(Number(b)/100)}c.q=q;c.p=q;d.textContent=q||'0';
};
H['wmtnr9l281j9cio']=function(ev,api,tools){var el=tools.el,run=tools.run,mem=tools.mem;
var c=mem,d=el('display');if(c.dn){c.p=c.q;c.dn=0}c.q=c.q||'0';c.p=c.p||'0';var e=c.q.slice(-1);if('+-*/'.indexOf(e)>=0){c.q=c.q.slice(0,-1);c.p=c.p.slice(0,-3)}c.p+=' ÷ ';c.q+='/';d.textContent=c.p
};
H['wmtnr9l281k46jv']=function(ev,api,tools){var el=tools.el,run=tools.run,mem=tools.mem;
var c=mem,d=el('display');if(c.dn){c.p='';c.q='';c.dn=0}c.q=c.q||'0';c.p=c.p||'0';if(c.q==='0'&&'7'!=='.'){c.p='';c.q=''}var i=Math.max(c.q.lastIndexOf('+'),c.q.lastIndexOf('-'),c.q.lastIndexOf('*'),c.q.lastIndexOf('/'));var ok='7'!=='.'||c.q.slice(i+1).indexOf('.')<0;if(ok){if(c.q===''&&'7'==='.'){c.p+='0.';c.q+='0.'}else if(i===c.q.length-1&&'7'==='.'){c.p+='0.';c.q+='0.'}else{c.p+='7';c.q+='7'}}d.textContent=c.p||'0';
};
H['wmtnr9l281ltfyc']=function(ev,api,tools){var el=tools.el,run=tools.run,mem=tools.mem;
var c=mem,d=el('display');if(c.dn){c.p='';c.q='';c.dn=0}c.q=c.q||'0';c.p=c.p||'0';if(c.q==='0'&&'8'!=='.'){c.p='';c.q=''}var i=Math.max(c.q.lastIndexOf('+'),c.q.lastIndexOf('-'),c.q.lastIndexOf('*'),c.q.lastIndexOf('/'));var ok='8'!=='.'||c.q.slice(i+1).indexOf('.')<0;if(ok){if(c.q===''&&'8'==='.'){c.p+='0.';c.q+='0.'}else if(i===c.q.length-1&&'8'==='.'){c.p+='0.';c.q+='0.'}else{c.p+='8';c.q+='8'}}d.textContent=c.p||'0';
};
H['wmtnr9l281m33po']=function(ev,api,tools){var el=tools.el,run=tools.run,mem=tools.mem;
var c=mem,d=el('display');if(c.dn){c.p='';c.q='';c.dn=0}c.q=c.q||'0';c.p=c.p||'0';if(c.q==='0'&&'9'!=='.'){c.p='';c.q=''}var i=Math.max(c.q.lastIndexOf('+'),c.q.lastIndexOf('-'),c.q.lastIndexOf('*'),c.q.lastIndexOf('/'));var ok='9'!=='.'||c.q.slice(i+1).indexOf('.')<0;if(ok){if(c.q===''&&'9'==='.'){c.p+='0.';c.q+='0.'}else if(i===c.q.length-1&&'9'==='.'){c.p+='0.';c.q+='0.'}else{c.p+='9';c.q+='9'}}d.textContent=c.p||'0';
};
H['wmtnr9l281nro4g']=function(ev,api,tools){var el=tools.el,run=tools.run,mem=tools.mem;
var c=mem,d=el('display');if(c.dn){c.p=c.q;c.dn=0}c.q=c.q||'0';c.p=c.p||'0';var e=c.q.slice(-1);if('+-*/'.indexOf(e)>=0){c.q=c.q.slice(0,-1);c.p=c.p.slice(0,-3)}c.p+=' × ';c.q+='*';d.textContent=c.p
};
H['wmtnr9l281orm5t']=function(ev,api,tools){var el=tools.el,run=tools.run,mem=tools.mem;
var c=mem,d=el('display');if(c.dn){c.p='';c.q='';c.dn=0}c.q=c.q||'0';c.p=c.p||'0';if(c.q==='0'&&'4'!=='.'){c.p='';c.q=''}var i=Math.max(c.q.lastIndexOf('+'),c.q.lastIndexOf('-'),c.q.lastIndexOf('*'),c.q.lastIndexOf('/'));var ok='4'!=='.'||c.q.slice(i+1).indexOf('.')<0;if(ok){if(c.q===''&&'4'==='.'){c.p+='0.';c.q+='0.'}else if(i===c.q.length-1&&'4'==='.'){c.p+='0.';c.q+='0.'}else{c.p+='4';c.q+='4'}}d.textContent=c.p||'0';
};
H['wmtnr9l281p87x3']=function(ev,api,tools){var el=tools.el,run=tools.run,mem=tools.mem;
var c=mem,d=el('display');if(c.dn){c.p='';c.q='';c.dn=0}c.q=c.q||'0';c.p=c.p||'0';if(c.q==='0'&&'5'!=='.'){c.p='';c.q=''}var i=Math.max(c.q.lastIndexOf('+'),c.q.lastIndexOf('-'),c.q.lastIndexOf('*'),c.q.lastIndexOf('/'));var ok='5'!=='.'||c.q.slice(i+1).indexOf('.')<0;if(ok){if(c.q===''&&'5'==='.'){c.p+='0.';c.q+='0.'}else if(i===c.q.length-1&&'5'==='.'){c.p+='0.';c.q+='0.'}else{c.p+='5';c.q+='5'}}d.textContent=c.p||'0';
};
H['wmtnr9l281q6806']=function(ev,api,tools){var el=tools.el,run=tools.run,mem=tools.mem;
var c=mem,d=el('display');if(c.dn){c.p='';c.q='';c.dn=0}c.q=c.q||'0';c.p=c.p||'0';if(c.q==='0'&&'6'!=='.'){c.p='';c.q=''}var i=Math.max(c.q.lastIndexOf('+'),c.q.lastIndexOf('-'),c.q.lastIndexOf('*'),c.q.lastIndexOf('/'));var ok='6'!=='.'||c.q.slice(i+1).indexOf('.')<0;if(ok){if(c.q===''&&'6'==='.'){c.p+='0.';c.q+='0.'}else if(i===c.q.length-1&&'6'==='.'){c.p+='0.';c.q+='0.'}else{c.p+='6';c.q+='6'}}d.textContent=c.p||'0';
};
H['wmtnr9l281rllvi']=function(ev,api,tools){var el=tools.el,run=tools.run,mem=tools.mem;
var c=mem,d=el('display');if(c.dn){c.p=c.q;c.dn=0}c.q=c.q||'0';c.p=c.p||'0';var e=c.q.slice(-1);if('+-*/'.indexOf(e)>=0){c.q=c.q.slice(0,-1);c.p=c.p.slice(0,-3)}c.p+=' − ';c.q+='-';d.textContent=c.p
};
H['wmtnr9l281sl4xm']=function(ev,api,tools){var el=tools.el,run=tools.run,mem=tools.mem;
var c=mem,d=el('display');if(c.dn){c.p='';c.q='';c.dn=0}c.q=c.q||'0';c.p=c.p||'0';if(c.q==='0'&&'1'!=='.'){c.p='';c.q=''}var i=Math.max(c.q.lastIndexOf('+'),c.q.lastIndexOf('-'),c.q.lastIndexOf('*'),c.q.lastIndexOf('/'));var ok='1'!=='.'||c.q.slice(i+1).indexOf('.')<0;if(ok){if(c.q===''&&'1'==='.'){c.p+='0.';c.q+='0.'}else if(i===c.q.length-1&&'1'==='.'){c.p+='0.';c.q+='0.'}else{c.p+='1';c.q+='1'}}d.textContent=c.p||'0';
};
H['wmtnr9l281tksv6']=function(ev,api,tools){var el=tools.el,run=tools.run,mem=tools.mem;
var c=mem,d=el('display');if(c.dn){c.p='';c.q='';c.dn=0}c.q=c.q||'0';c.p=c.p||'0';if(c.q==='0'&&'2'!=='.'){c.p='';c.q=''}var i=Math.max(c.q.lastIndexOf('+'),c.q.lastIndexOf('-'),c.q.lastIndexOf('*'),c.q.lastIndexOf('/'));var ok='2'!=='.'||c.q.slice(i+1).indexOf('.')<0;if(ok){if(c.q===''&&'2'==='.'){c.p+='0.';c.q+='0.'}else if(i===c.q.length-1&&'2'==='.'){c.p+='0.';c.q+='0.'}else{c.p+='2';c.q+='2'}}d.textContent=c.p||'0';
};
H['wmtnr9l281usc9t']=function(ev,api,tools){var el=tools.el,run=tools.run,mem=tools.mem;
var c=mem,d=el('display');if(c.dn){c.p='';c.q='';c.dn=0}c.q=c.q||'0';c.p=c.p||'0';if(c.q==='0'&&'3'!=='.'){c.p='';c.q=''}var i=Math.max(c.q.lastIndexOf('+'),c.q.lastIndexOf('-'),c.q.lastIndexOf('*'),c.q.lastIndexOf('/'));var ok='3'!=='.'||c.q.slice(i+1).indexOf('.')<0;if(ok){if(c.q===''&&'3'==='.'){c.p+='0.';c.q+='0.'}else if(i===c.q.length-1&&'3'==='.'){c.p+='0.';c.q+='0.'}else{c.p+='3';c.q+='3'}}d.textContent=c.p||'0';
};
H['wmtnr9l281vy6ib']=function(ev,api,tools){var el=tools.el,run=tools.run,mem=tools.mem;
var c=mem,d=el('display');if(c.dn){c.p=c.q;c.dn=0}c.q=c.q||'0';c.p=c.p||'0';var e=c.q.slice(-1);if('+-*/'.indexOf(e)>=0){c.q=c.q.slice(0,-1);c.p=c.p.slice(0,-3)}c.p+=' + ';c.q+='+';d.textContent=c.p
};
H['wmtnr9l281woh84']=function(ev,api,tools){var el=tools.el,run=tools.run,mem=tools.mem;
var c=mem,d=el('display');if(c.dn){c.p='';c.q='';c.dn=0}c.q=c.q||'0';c.p=c.p||'0';if(c.q==='0'&&'0'!=='.'){c.p='';c.q=''}var i=Math.max(c.q.lastIndexOf('+'),c.q.lastIndexOf('-'),c.q.lastIndexOf('*'),c.q.lastIndexOf('/'));var ok='0'!=='.'||c.q.slice(i+1).indexOf('.')<0;if(ok){if(c.q===''&&'0'==='.'){c.p+='0.';c.q+='0.'}else if(i===c.q.length-1&&'0'==='.'){c.p+='0.';c.q+='0.'}else{c.p+='0';c.q+='0'}}d.textContent=c.p||'0';
};
H['wmtnr9l281xzu6u']=function(ev,api,tools){var el=tools.el,run=tools.run,mem=tools.mem;
var c=mem,d=el('display');if(c.dn){c.p='';c.q='';c.dn=0}c.q=c.q||'0';c.p=c.p||'0';if(c.q==='0'&&'.'!=='.'){c.p='';c.q=''}var i=Math.max(c.q.lastIndexOf('+'),c.q.lastIndexOf('-'),c.q.lastIndexOf('*'),c.q.lastIndexOf('/'));var ok='.'!=='.'||c.q.slice(i+1).indexOf('.')<0;if(ok){if(c.q===''&&'.'==='.'){c.p+='0.';c.q+='0.'}else if(i===c.q.length-1&&'.'==='.'){c.p+='0.';c.q+='0.'}else{c.p+='.';c.q+='.'}}d.textContent=c.p||'0';
};
H['wmtnr9l281yye5x']=function(ev,api,tools){var el=tools.el,run=tools.run,mem=tools.mem;
var c=mem,d=el('display');try{var r=run(c.q),s=String(Math.round(r*1e10)/1e10);c.p=s;c.q=s;c.dn=1;d.textContent=s}catch(err){d.textContent='err';c.p='0';c.q='0';c.dn=0};
};
})();
</script>
</body>
</html>
"""
]


def main():
    port = 5200
    no_open = False
    for arg in sys.argv[1:]:
        if arg == "--no-open":
            no_open = True
        elif arg.isdigit():
            port = int(arg)
    port = int(os.environ.get("PORT", port))
    try:
        import lumiora.web
    except Exception:
        lumiora.web = None
    if lumiora.web is not None:
        lumiora.web.open_app(HERE, APP_TITLE, WINDOWS, WINDOW_PAGES,
                             style_css=STYLE_CSS, port=port, no_open=no_open)
        return
    print()
    print("  lumiora is not installed — desktop windows need it.")
    print("  Install it once with:  pip install lumiora")
    page = HERE / "index.html"
    if not no_open and page.is_file():
        webbrowser.open(page.resolve().as_uri())
    print("  Opened index.html in your browser (or run:  python run_web.py)")


if __name__ == "__main__":
    main()
