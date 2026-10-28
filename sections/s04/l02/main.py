"""A tiny in-memory HTTP API for the Section 04 HTTP exercise."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import parse_qs, urlparse


NOTES = {
    "123": {"id": "123", "title": "調査メモ", "body": "API応答を確認する"},
}
NEXT_ID = 124


class NotesHandler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        parts = path.strip("/").split("/")
        if len(parts) == 2 and parts[0] == "notes":
            note = NOTES.get(parts[1])
            if note is not None:
                if parse_qs(parsed.query).get("view") == ["compact"]:
                    note = {"id": note["id"], "title": note["title"]}
                self.send_json(200, note)
            else:
                self.send_json(404, {"error": "note_not_found", "id": parts[1]})
            return
        self.send_json(404, {"error": "route_not_found"})

    def do_POST(self):
        global NEXT_ID
        if urlparse(self.path).path != "/notes":
            self.send_json(404, {"error": "route_not_found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError):
            self.send_json(400, {"error": "invalid_json"})
            return

        if not isinstance(payload, dict) or not isinstance(payload.get("title"), str) or not payload["title"].strip():
            self.send_json(400, {"error": "title_required"})
            return

        note_id = str(NEXT_ID)
        NEXT_ID += 1
        note = {"id": note_id, "title": payload["title"].strip(), "body": payload.get("body", "")}
        NOTES[note_id] = note
        self.send_json(201, note)

    def do_PUT(self):
        self.send_unsupported_method()

    def send_unsupported_method(self):
        self.send_response(405)
        self.send_header("Allow", "GET, POST")
        body = json.dumps({"error": "method_not_allowed"}).encode("utf-8")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Keep the exercise output focused on the HTTP responses.
        pass


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8000), NotesHandler)
    print("API ready: http://127.0.0.1:8000 (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
