"""Optional warm server: keeps the Whisper model loaded so each transcription skips the load time.

Binds to 127.0.0.1 only. shortcut: single-threaded and unauthenticated, fine for one local user,
add a token if the machine is shared.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

from tgmedia import audio

HOST, PORT = "127.0.0.1", 8765


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            if not os.path.isfile(req["file"]):
                raise FileNotFoundError(req["file"])
            result = audio.transcribe(req["file"], req.get("model", "small"), req.get("language"))
            status, body = 200, {"language": result.language, "text": result.text}
        except (KeyError, ValueError, FileNotFoundError, RuntimeError) as exc:
            status, body = 400, {"error": str(exc)}
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


def serve(model: str = "small", port: int = PORT) -> None:
    audio._load_model(model)  # load once, up front
    HTTPServer((HOST, port), _Handler).serve_forever()


def remote_transcribe(path: str, model: str, language: str | None, port: int = PORT) -> audio.Transcript | None:
    """Ask the warm server; return None if it is not running so the caller can fall back."""
    payload = json.dumps({"file": os.path.abspath(path), "model": model, "language": language}).encode()
    req = urllib.request.Request(f"http://{HOST}:{port}/", payload, {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(json.load(exc).get("error", "server error")) from exc
    except (urllib.error.URLError, ConnectionError, TimeoutError):
        return None
    return audio.Transcript(data["language"], data["text"])
