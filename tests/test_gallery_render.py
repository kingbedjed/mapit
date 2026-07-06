#!/usr/bin/env python3
"""Render the gallery in a real headless browser and confirm each example draws
without errors. Serves web/ on a throwaway local port (self-contained). Needs
the internet (Three.js loads from a CDN). Auto-skips if Playwright or a browser
isn't available, so the fast tests still pass without them."""
import functools
import http.server
import os
import socketserver
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "..", "web")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "builders"))
from gallery import EXAMPLES        # noqa: E402
from mapit_url import build_map_url  # noqa: E402


class _Handler(http.server.SimpleHTTPRequestHandler):
    # ensure ES modules are served with a JavaScript MIME type
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".js": "application/javascript"}

    def log_message(self, *a):  # quiet
        pass


def _serve(directory):
    handler = functools.partial(_Handler, directory=directory)
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def test_examples_render():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("SKIP: playwright not installed")
        return

    httpd, port = _serve(WEB)
    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch()
            except Exception as e:  # no browser downloaded
                print(f"SKIP: no chromium ({e})")
                return
            for ex in EXAMPLES:
                page = browser.new_context().new_page()
                logs = []
                page.on("console", lambda m: logs.append(m.text))
                page.on("pageerror", lambda e: logs.append("ERR:" + str(e)))
                url = build_map_url(**ex["kwargs"]).replace(
                    "https://jeddoman.com/mapit/", f"http://127.0.0.1:{port}/")
                page.goto(url, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(3000)
                made = [l for l in logs if "Map created" in l]
                errs = [l for l in logs if l.startswith("ERR")]
                assert made, f"{ex['name']}: did not render (last logs: {logs[-3:]})"
                assert not errs, f"{ex['name']}: page error {errs[:1]}"
                page.close()
            browser.close()
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    test_examples_render()
    print("✅ gallery render tests passed (or skipped)")
