from __future__ import annotations

import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from knowledge_engine import KnowledgeEngine


ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"
ENGINE = KnowledgeEngine()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/health":
            self._json({"status": "ok", "documents": len(ENGINE.documents)})
        elif path == "/api/users":
            self._json({"users": ENGINE.public_users()})
        else:
            super().do_GET()

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/ask":
            self._json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 16_384:
                self._json({"error": "Payload too large"}, HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
                return
            body = json.loads(self.rfile.read(length) or b"{}")
            result = ENGINE.ask(str(body.get("user_id", "")), str(body.get("question", "")))
            self._json(result.as_dict())
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json({"error": "Invalid JSON"}, HTTPStatus.BAD_REQUEST)

    def log_message(self, format: str, *args) -> None:
        print(f"[http] {self.address_string()} {format % args}")

    def _json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)


if __name__ == "__main__":
    address = ("127.0.0.1", 8000)
    print(f"Appota Knowledge MVP đang chạy tại http://{address[0]}:{address[1]}")
    ThreadingHTTPServer(address, Handler).serve_forever()
