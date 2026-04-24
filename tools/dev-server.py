#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SITE_DIR = Path("/Users/user/Documents/Codex/2026-04-19-finder-plugin-computer-use-openai-bundled/gallery-site")
PUBLIC_DIR = SITE_DIR / "public"
BUILD_SCRIPT = SITE_DIR / "tools" / "build-gallery.py"
HOST = "127.0.0.1"
PORT = 8000


class GalleryHandler(SimpleHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path != "/api/rebuild":
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return

        try:
            completed = subprocess.run(
                ["python3", str(BUILD_SCRIPT)],
                cwd=str(SITE_DIR),
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as error:
            payload = {
                "ok": False,
                "error": error.stderr.strip() or error.stdout.strip() or "重建失敗",
            }
            response = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)
            return

        payload = {
            "ok": True,
            "message": completed.stdout.strip() or "重建完成",
        }
        response = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)


def main() -> None:
    handler = partial(GalleryHandler, directory=str(PUBLIC_DIR))
    server = ThreadingHTTPServer((HOST, PORT), handler)
    print(f"Serving gallery at http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping gallery server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
