"""Dev server for viz/.

Runs http.server on 127.0.0.1:8765, serves the viz/ directory, opens the
default browser. Sends no-cache headers so a plain refresh always reflects
the latest edits to viz/*.js or viz/index.html.

Usage: python3 scripts/serve_viz.py
"""

import http.server
import pathlib
import socketserver
import sys
import webbrowser


HOST = "127.0.0.1"
PORT = 8765
ROOT = pathlib.Path(__file__).resolve().parent.parent / "viz"


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def main() -> int:
    if not ROOT.is_dir():
        print(f"viz directory not found: {ROOT}", file=sys.stderr)
        return 1

    handler = lambda *a, **kw: NoCacheHandler(*a, directory=str(ROOT), **kw)
    with socketserver.TCPServer((HOST, PORT), handler) as httpd:
        url = f"http://{HOST}:{PORT}/"
        print(f"serving {ROOT} at {url}  (Ctrl-C to quit)")
        try:
            webbrowser.open(url)
        except Exception:
            pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nshutting down")
    return 0


if __name__ == "__main__":
    sys.exit(main())
