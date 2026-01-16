from flask import Flask, render_template, request, send_file
import os
import subprocess
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "static/output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔥 Ghostscript direct path (Windows)
GS_PATH = r"C:\Program Files\gs\gs10.06.0\bin\gswin64c.exe"


def compress_pdf_gs(input_pdf, output_pdf):
    subprocess.run([
        GS_PATH,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/screen",      # maximum compression
        "-dNOPAUSE",
        "-dBATCH",
        "-dDownsampleColorImages=true",
        "-dColorImageResolution=72",
        "-dGrayImageResolution=72",
        "-dMonoImageResolution=72",
        f"-sOutputFile={output_pdf}",
        input_pdf
    ], check=True)


# 🔥 DOUBLE PASS (CloudConvert-style)
def compress_twice(input_pdf, output_pdf):
    temp_pdf = input_pdf.replace(".pdf", "_temp.pdf")

    compress_pdf_gs(input_pdf, temp_pdf)
    compress_pdf_gs(temp_pdf, output_pdf)

    if os.path.exists(temp_pdf):
        os.remove(temp_pdf)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/compress", methods=["POST"])
def compress_pdf():
    if "pdf" not in request.files:
        return "No file uploaded", 400

    file = request.files["pdf"]

    uid = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f"{uid}_input.pdf")
    output_path = os.path.join(UPLOAD_FOLDER, f"{uid}_compressed.pdf")

    file.save(input_path)

    # 🔥 real compression
    compress_twice(input_path, output_path)

    return send_file(
        output_path,
        as_attachment=True,
        download_name="compressed.pdf",
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    app.run(debug=True)
