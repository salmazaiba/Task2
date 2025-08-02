
from flask import Flask, request, jsonify, redirect, abort
from app.storage import store, increment_click
from app.utils import generate_short_code
from app.validators import is_valid_url
from datetime import datetime

app = Flask(_name_)

@app.route("/")
def health_check():
    return {"status": "ok"}

@app.route("/api/shorten", methods=["POST"])
def shorten_url():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "Missing 'url' in request body"}), 400

    long_url = data["url"]
    if not is_valid_url(long_url):
        return jsonify({"error": "Invalid URL"}), 400

    short_code = generate_short_code()
    store[short_code] = {
        "url": long_url,
        "created_at": datetime.utcnow(),
        "clicks": 0
    }

    return jsonify({
        "short_code": short_code,
        "short_url": f"http://localhost:5000/{short_code}"
    }), 201

@app.route("/<short_code>", methods=["GET"])
def redirect_url(short_code):
    if short_code not in store:
        abort(404)
    increment_click(short_code)
    return redirect(store[short_code]["url"])

@app.route("/api/stats/<short_code>", methods=["GET"])
def get_stats(short_code):
    if short_code not in store:
        return jsonify({"error": "Short code not found"}), 404

    data = store[short_code]
    return jsonify({
        "url": data["url"],
        "clicks": data["clicks"],
        "created_at": data["created_at"].isoformat()
    })