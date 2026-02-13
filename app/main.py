import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, send_file

from app.parser.pdf_parser import extract_text_from_pdf
from app.parser.docx_parser import extract_text_from_docx
from app.parser.image_parser import extract_text_from_image
from app.parser.extractor import extract_row
from app.services.excel_service import append_row


# -------------------------------------------------
# PATH SETUP
# -------------------------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

app = Flask(
    __name__,
    template_folder=os.path.join(PROJECT_ROOT, "templates"),
    static_folder=os.path.join(PROJECT_ROOT, "static")
)

UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "uploads")
OUTPUT_FOLDER = os.path.join(PROJECT_ROOT, "output")
EXCEL_PATH = os.path.join(OUTPUT_FOLDER, "resume_data.xlsx")
BACKUP_EXCEL_PATH = os.path.join(OUTPUT_FOLDER, "resume_data_backup.xlsx")

ALLOWED_EXTENSIONS = {"pdf", "docx", "png", "jpg", "jpeg"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def allowed_file(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


# -------------------------------------------------
# ROUTES
# -------------------------------------------------
@app.route("/resume-parser", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def index():
    table_data = []

    if request.method == "POST":
        file = request.files.get("resume")

        if file and allowed_file(file.filename):

            filename = file.filename
            ext = filename.rsplit(".", 1)[1].lower()
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            file.save(file_path)

            try:
                # -------- STRICT TYPE ROUTING --------
                if ext == "pdf":
                    text = extract_text_from_pdf(file_path)

                elif ext == "docx":
                    text = extract_text_from_docx(file_path)

                elif ext in {"png", "jpg", "jpeg"}:
                    text = extract_text_from_image(file_path)

                else:
                    return render_template(
                        "index.html",
                        data=table_data,
                        error="Unsupported file format."
                    )

                if not text or text.strip() == "":
                    return render_template(
                        "index.html",
                        data=table_data,
                        error="File could not be processed. No readable text found."
                    )

                row = extract_row(text)
                df = append_row(row, EXCEL_PATH)
                table_data = df.to_dict(orient="records")

            except Exception as e:
                print("Parsing error:", e)
                return render_template(
                    "index.html",
                    data=table_data,
                    error="File could not be processed. Please upload a valid resume."
                )

    # -------- LOAD EXISTING DATA --------
    elif os.path.exists(EXCEL_PATH):
        df = pd.read_excel(EXCEL_PATH)
        table_data = df.to_dict(orient="records")

    # -------- NORMALIZE DISPLAY --------
    for row in table_data:
        edu = row.get("Education", "")
        if not isinstance(edu, str) or edu.strip() == "" or str(edu).lower() == "nan":
            row["Education"] = "No education data available"

        cert = row.get("Certifications", "")
        if not isinstance(cert, str) or cert.strip() == "" or str(cert).lower() == "nan":
            row["Certifications"] = "No certification data available"

    return render_template("index.html", data=table_data)


@app.route("/delete/<int:row_id>")
def delete_row(row_id):
    if os.path.exists(EXCEL_PATH):
        df = pd.read_excel(EXCEL_PATH)

        df.to_excel(BACKUP_EXCEL_PATH, index=False)

        if 0 <= row_id < len(df):
            df.drop(index=row_id, inplace=True)
            df.reset_index(drop=True, inplace=True)
            df.to_excel(EXCEL_PATH, index=False)

    return redirect(url_for("index"))


@app.route("/reset", methods=["POST"])
def reset_table():
    if os.path.exists(EXCEL_PATH):
        os.remove(EXCEL_PATH)

    if os.path.exists(BACKUP_EXCEL_PATH):
        os.remove(BACKUP_EXCEL_PATH)

    return redirect(url_for("index"))


@app.route("/undo")
def undo_delete():
    if os.path.exists(BACKUP_EXCEL_PATH):
        os.replace(BACKUP_EXCEL_PATH, EXCEL_PATH)

    return redirect(url_for("index"))


@app.route("/download")
def download_excel():
    if os.path.exists(EXCEL_PATH):
        return send_file(EXCEL_PATH, as_attachment=True)

    return redirect(url_for("index"))


# -------------------------------------------------
# RUN
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
