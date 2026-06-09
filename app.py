from flask import Flask, request, redirect, jsonify, render_template, abort
import random
import string

app = Flask(__name__)

# In-memory storage: { "abc123": {"url": "https://...", "clicks": 0} }
url_map = {}


def generate_code(length=6):
    """Generate a unique 6-char alphanumeric code."""
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(chars, k=length))
        if code not in url_map: # retry on collision (extremely rare)
            return code


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json()
    long_url = data.get("url", "").strip()

    # Basic validation — must start with http:// or https://
    if not long_url.startswith(("http://", "https://")):
        return jsonify({"error": "Invalid URL. Must start with http:// or https://"}), 400

    code = generate_code()
    url_map[code] = {"url": long_url, "clicks": 0}

    short_url = request.host_url + "r/" + code
    return jsonify({"short_url": short_url, "code": code})


@app.route("/r/<code>")
def redirect_to_url(code):
    entry = url_map.get(code)
    if not entry:
        abort(404)
    entry["clicks"] += 1
    return redirect(entry["url"], code=302)


@app.route("/stats")
def stats():
    data = [
        {"code": code, "url": v["url"], "clicks": v["clicks"]}
        for code, v in url_map.items()
    ]
    return jsonify(data)


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Short code not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)