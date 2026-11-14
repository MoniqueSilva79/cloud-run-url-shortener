"""Encurtador de URL – Flask + Firestore, pronto para Cloud Run."""
import os
import secrets
from urllib.parse import urlparse

from flask import Flask, abort, jsonify, redirect, request
from google.cloud import firestore

app = Flask(__name__)
db = firestore.Client()
links = db.collection("links")


def valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/shorten")
def shorten():
    url = (request.get_json(silent=True) or {}).get("url", "")
    if not valid_url(url):
        return jsonify(error="URL inválida"), 400

    code = secrets.token_urlsafe(5)[:7]
    while links.document(code).get().exists:
        code = secrets.token_urlsafe(5)[:7]

    links.document(code).set({"url": url, "clicks": 0, "created": firestore.SERVER_TIMESTAMP})
    return jsonify(code=code, short_url=f"{request.host_url}{code}"), 201


@app.get("/<code>")
def go(code):
    doc = links.document(code)
    snap = doc.get()
    if not snap.exists:
        abort(404)
    doc.update({"clicks": firestore.Increment(1)})
    return redirect(snap.get("url"), code=302)


@app.get("/stats/<code>")
def stats(code):
    snap = links.document(code).get()
    if not snap.exists:
        abort(404)
    return jsonify(code=code, url=snap.get("url"), clicks=snap.get("clicks"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
