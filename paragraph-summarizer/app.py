from __future__ import annotations
from flask import Flask, render_template, request
from utils.summarizer import summarize

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    summary = ""
    error = ""
    text = ""
    ratio = ""
    sentences = ""
    max_chars = ""

    if request.method == "POST":
        text = (request.form.get("text") or "").strip()
        ratio_str = (request.form.get("ratio") or "").strip()
        sentences_str = (request.form.get("sentences") or "").strip()
        max_chars_str = (request.form.get("max_chars") or "").strip()

        try:
            ratio = float(ratio_str) if ratio_str else None
            if ratio is not None and not (0 < ratio <= 1):
                raise ValueError("Ratio must be between 0 and 1.")
        except ValueError:
            error = "Invalid ratio. Use a number between 0 and 1 (e.g., 0.3)."

        try:
            sentences = int(sentences_str) if sentences_str else None
            if sentences is not None and sentences <= 0:
                raise ValueError("Sentences must be positive.")
        except ValueError:
            error = "Invalid sentence count. Use a positive integer."

        try:
            max_chars = int(max_chars_str) if max_chars_str else None
            if max_chars is not None and max_chars <= 0:
                raise ValueError("Max chars must be positive.")
        except ValueError:
            error = "Invalid max chars. Use a positive integer."

        if not error:
            if not text:
                error = "Please paste a paragraph to summarize."
            else:
                summary = summarize(text, ratio=ratio, sentences=sentences, max_chars=max_chars)

    return render_template(
        "index.html",
        summary=summary,
        error=error,
        text=text,
        ratio=ratio,
        sentences=sentences,
        max_chars=max_chars
    )

if __name__ == "__main__":
    app.run(debug=True)
