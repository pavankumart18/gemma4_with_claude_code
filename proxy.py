"""
Proxy: sits on :11435, logs every request body to proxy_log.json, forwards to Ollama :11434
"""
import http.server
import urllib.request
import json
import os

LOG = "proxy_log.jsonl"
TARGET = "http://localhost:11434"

class Proxy(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        # Log request
        with open(LOG, "a", encoding="utf-8") as f:
            entry = {"path": self.path, "body": json.loads(body) if body else None}
            f.write(json.dumps(entry) + "\n")

        # Forward to Ollama
        req = urllib.request.Request(
            TARGET + self.path,
            data=body,
            headers={k: v for k, v in self.headers.items()
                     if k.lower() not in ("host", "content-length")},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                resp_body = resp.read()
                self.send_response(resp.status)
                for k, v in resp.getheaders():
                    if k.lower() != "transfer-encoding":
                        self.send_header(k, v)
                self.end_headers()
                self.wfile.write(resp_body)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def log_message(self, *_):
        pass

if __name__ == "__main__":
    if os.path.exists(LOG):
        os.remove(LOG)
    print("Proxy on :11435 → Ollama :11434  (logging to proxy_log.jsonl)")
    http.server.HTTPServer(("localhost", 11435), Proxy).serve_forever()
