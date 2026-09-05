"""Lumiora — webview desktop apps for your HTML layouts.

``lumiora.web`` is a real desktop launcher: it opens exported (or
hand-written) HTML layouts in frameless, per-pixel-transparent windows
rendered by WebView2 through DirectComposition — pure Python stdlib,
nothing else to install. Without the WebView2 runtime it falls back to a
localhost browser server, so it works on any OS with zero dependencies.

    import lumiora.web

    lumiora.web.demo()            # built-in sample app (two windows)
    lumiora.web.run("my-app")     # layout folder -> real desktop app
    lumiora.web.open_app(...)     # in-memory windows+pages -> desktop app
    lumiora.web.serve("my-app")   # same layout -> plain browser server

or from the command line:

    python -m lumiora.web --demo
    python -m lumiora.web my-app

LUMIORA Builder exports are thin launchers built on this: their main.py
holds the layout (per-window specs, HTML pages, css) and hands it to
``lumiora.web.open_app``, so every window opens as its own real desktop
window with working drag / minimize / maximize / close.
"""

__version__ = "2.3.0"

__all__ = ["web", "__version__"]


def __getattr__(name):
    # lazy: `import lumiora.web` / `python -m lumiora.web` must not double
    # import the module (python -m re-runs an eagerly imported submodule)
    if name == "web":
        from . import web  # noqa: PLC0415
        return web
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
