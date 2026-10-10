#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyjwt[crypto]"]
# ///
"""Minimal stand-in for api.github.com's installation token endpoint.

Usage: fake_github_api.py <mode> <log-file> <public-key-pem>
       fake_github_api.py --check   (imports jwt and exits 0; warms uv's cache)
mode: ok | empty-token | unauthorized
Prints the bound port on stdout once listening.
Every request's App JWT is verified against <public-key-pem> (RS256, iss "7");
a missing or invalid JWT gets a 401.
Every request appends one line to <log-file>:
  POST PATH Bearer OK|BADJWT accept-ok|accept-missing
"""

import datetime
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import jwt

if sys.argv[1:] == ["--check"]:
    sys.exit(0)

MODE, LOG, PUB = sys.argv[1], sys.argv[2], Path(sys.argv[3]).read_text()
# Deliberately odd (47 min 13 s): a client that ignores expires_at and assumes
# GitHub's usual one hour cannot match it by accident.
LIFETIME_SECONDS = 2833


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):  # keep the test output clean
        pass

    def do_POST(self):
        scheme, _, token = self.headers.get("Authorization", "").partition(" ")
        try:
            if scheme != "Bearer":
                raise jwt.InvalidTokenError("not a Bearer credential")
            jwt.decode(
                token,
                PUB,
                algorithms=["RS256"],
                issuer="7",
                leeway=60,
                options={"require": ["iat", "exp", "iss"]},
            )
            verdict = "OK"
        except jwt.PyJWTError:
            verdict = "BADJWT"
        accept = (
            "accept-ok"
            if self.headers.get("Accept") == "application/vnd.github+json"
            else "accept-missing"
        )
        with Path(LOG).open("a") as f:
            f.write(f"POST {self.path} Bearer {verdict} {accept}\n")
        if verdict != "OK" or MODE == "unauthorized":
            self.send_response(401)
            self.end_headers()
            return
        expires = (
            datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=LIFETIME_SECONDS)
        ).replace(microsecond=0)
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
