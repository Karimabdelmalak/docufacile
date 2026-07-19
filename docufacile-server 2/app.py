"""
DocuFacile — Serveur de conversion de documents
Word → PDF : LibreOffice (rendu quasi identique à l'original)
PDF → Word : pdf2docx (conserve la mise en page, les tableaux et les images)
"""
import os
import shutil
import subprocess
import tempfile
import uuid

from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
from pdf2docx import Converter

app = Flask(__name__, static_folder="static")
CORS(app)

MAX_SIZE = 50 * 1024 * 1024  # 50 Mo
app.config["MAX_CONTENT_LENGTH"] = MAX_SIZE

WORD_EXTS = {".docx", ".doc", ".odt", ".rtf", ".txt"}


def _save_upload(upload, allowed_exts):
    """Sauvegarde le fichier reçu dans un dossier temporaire isolé."""
    ext = os.path.splitext(upload.filename or "")[1].lower()
    if ext not in allowed_exts:
        raise ValueError(f"Format non accepté : {ext or 'inconnu'}")
    workdir = tempfile.mkdtemp(prefix="docufacile-")
    # nom neutre pour éviter tout problème de caractères spéciaux
    path = os.path.join(workdir, f"input-{uuid.uuid4().hex[:8]}{ext}")
    upload.save(path)
    return workdir, path


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/word-to-pdf")
def word_to_pdf():
    if "file" not in request.files:
        return jsonify({"error": "Aucun fichier reçu"}), 400
    try:
        workdir, src = _save_upload(request.files["file"], WORD_EXTS)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    try:
        result = subprocess.run(
            ["soffice", "--headless", "--convert-to", "pdf", "--outdir", workdir, src],
            capture_output=True, timeout=120,
            env={**os.environ, "HOME": workdir},  # profil LibreOffice isolé
        )
        pdf_path = os.path.splitext(src)[0] + ".pdf"
        if result.returncode != 0 or not os.path.exists(pdf_path):
            return jsonify({"error": "Échec de la conversion LibreOffice"}), 500
        original = os.path.splitext(request.files["file"].filename)[0] or "document"
        return send_file(pdf_path, as_attachment=True,
                         download_name=f"{original}.pdf", mimetype="application/pdf")
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Conversion trop longue (délai dépassé)"}), 504
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


@app.post("/api/pdf-to-word")
def pdf_to_word():
    if "file" not in request.files:
        return jsonify({"error": "Aucun fichier reçu"}), 400
    try:
        workdir, src = _save_upload(request.files["file"], {".pdf"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    try:
        out = os.path.join(workdir, "output.docx")
        cv = Converter(src)
        cv.convert(out)
        cv.close()
        if not os.path.exists(out):
            return jsonify({"error": "Échec de la conversion PDF → Word"}), 500
        original = os.path.splitext(request.files["file"].filename)[0] or "document"
        return send_file(
            out, as_attachment=True, download_name=f"{original}.docx",
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except Exception as e:
        return jsonify({"error": f"Conversion impossible : {e}"}), 500
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
