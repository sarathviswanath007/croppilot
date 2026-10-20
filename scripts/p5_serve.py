"""Run the CropPilot web app locally: build web/ (p5_build_web) and serve it.

Usage: python3 scripts/p5_serve.py [port]      then open http://localhost:8000
Stop with Ctrl+C.
"""
import functools
import http.server
import sys

from p5_build_web import WEB, build


def main():
    build()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(WEB))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"CropPilot running at http://localhost:{port}  (Ctrl+C to stop)")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
