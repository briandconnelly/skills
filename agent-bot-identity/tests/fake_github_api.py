"""Minimal stand-in for api.github.com's installation token endpoint.

Usage: fake_github_api.py <mode> <log-file>
mode: ok | empty-token | unauthorized
Prints the bound port on stdout once listening.
Every request appends one line to <log-file>: METHOD PATH AUTH-SCHEME JWT-SEGMENTS
"""

import datetime
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

MODE, LOG = sys.argv[1], sys.argv[2]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):  # keep the test output clean
        pass

    def do_POST(self):
        auth = self.headers.get("Authorization", "")
        scheme, _, token = auth.partition(" ")
        with Path(LOG).open("a") as f:
            f.write(f"POST {self.path} {scheme} {len(token.split('.'))}\n")
        if MODE == "unauthorized":
            self.send_response(401)
            self.end_headers()
            return
        expires = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1)).replace(
            microsecond=0
        )
        body = {
            "token": "" if MODE == "empty-token" else "ghs_fakemint",
            "expires_at": expires.isoformat().replace("+00:00", "Z"),
        }
        data = json.dumps(body).encode()
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


server = HTTPServer(("127.0.0.1", 0), Handler)
print(server.server_address[1], flush=True)
server.serve_forever()
