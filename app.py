import io
from pathlib import Path

from flask import Flask, abort, render_template, request, send_file
from werkzeug.exceptions import HTTPException

from recolor import PALETTE, recolor_pdf

MAX_UPLOAD_MB = 50
DEFAULT_COLOR = "blue"

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024


@app.get("/")
def index():
    return render_template("index.html", palette=PALETTE, default=DEFAULT_COLOR)


@app.post("/convert")
def convert():
    upload = _read_upload()
    color_key = _read_color()
    try:
        result = recolor_pdf(upload.read(), PALETTE[color_key][1])
    except Exception:
        abort(422, "This file could not be processed. Make sure it is a valid PDF.")
    return send_file(
        io.BytesIO(result),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=_output_name(upload.filename, color_key),
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.errorhandler(HTTPException)
def handle_error(error: HTTPException):
    return render_template("error.html", error=error), error.code


def _read_upload():
    upload = request.files.get("pdf")
    if upload is None or not upload.filename:
        abort(400, "No file was selected.")
    return upload


def _read_color() -> str:
    key = request.form.get("color", DEFAULT_COLOR)
    if key not in PALETTE:
        abort(400, "That color is not available.")
    return key


def _output_name(filename: str, color_key: str) -> str:
    stem = Path(filename).stem or "document"
    return f"{stem}-{color_key}.pdf"
