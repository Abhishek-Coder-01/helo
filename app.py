from flask import Flask, render_template, request, send_file
import os
import subprocess
import uuid
import shutil

app = Flask(__name__)

# Upload/output folder
UPLOAD_FOLDER = "static/output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔥 Auto-detect Ghostscript (works on Docker/Linux/Render)
GS_PATH = shutil.which("gs")
if GS_PATH is None:
    raise RuntimeError("Ghostscript not found. Make sure it is installed.")

def compress_pdf_gs(input_pdf, output_pdf):
    """
    Strong compression (CloudConvert-like)
    """
    subprocess.run(
        [
            GS_PATH,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/screen",
            "-dNOPAUSE",
            "-dBATCH",
            "-dDownsampleColorImages=true",
            "-dColorImageResolution=72",
            "-dGrayImageResolution=72",
            "-dMonoImageResolution=72",
            f"-sOutputFile={output_pdf}",
            input_pdf
        ],
        check=True
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/compress", methods=["POST"])
def compress_pdf():
    if "pdf" not in request.files:
        return "No file uploaded", 400

    file = request.files["pdf"]
    if file.filename == "":
        return "No selected file", 400

    uid = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f"{uid}_input.pdf")
    output_path = os.path.join(UPLOAD_FOLDER, f"{uid}_compressed.pdf")

    # Save uploaded PDF
    file.save(input_path)

    # Compress using Ghostscript
    compress_pdf_gs(input_path, output_path)

    # Send compressed PDF
    return send_file(
        output_path,
        as_attachment=True,
        download_name="compressed.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    # 🔥 REQUIRED for Docker/Render
    app.run(host="0.0.0.0", port=5000)
