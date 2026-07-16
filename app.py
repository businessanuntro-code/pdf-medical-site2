import os

from flask import Flask, render_template, request, redirect, flash

import config

from parser.extractor import extract_zip
from parser.analyzer import analyze_extracted_folder
from parser.article_detector import detect_articles



app = Flask(__name__)

app.secret_key = "pdf-medical-site-secret-key"


app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH



for folder in [
    config.UPLOAD_FOLDER,
    config.EXTRACT_FOLDER,
    config.PROCESSED_FOLDER,
    config.OUTPUT_FOLDER,
    config.DATABASE_FOLDER
]:
    os.makedirs(folder, exist_ok=True)




def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in config.ALLOWED_EXTENSIONS
    )





def find_html_folder(base_folder):

    for root, dirs, files in os.walk(base_folder):

        html_files = [
            f for f in files
            if f.lower().endswith(".html")
        ]

        if html_files:
            return root


    return None





@app.route("/")
def home():

    return render_template("home.html")





@app.route("/dashboard")
def dashboard():

    return render_template("dashboard.html")





@app.route("/upload", methods=["GET", "POST"])
def upload():


    if request.method == "POST":


        if "revista" not in request.files:

            flash("Nu a fost selectată arhiva.")

            return redirect(request.url)



        file = request.files["revista"]



        if file.filename == "":

            flash("Nu există fișier selectat.")

            return redirect(request.url)



        if not allowed_file(file.filename):

            flash("Este permis doar ZIP.")

            return redirect(request.url)



        filename = file.filename



        zip_path = os.path.join(
            config.UPLOAD_FOLDER,
            filename
        )


        file.save(zip_path)



        # 1. Dezarhivare

        extract_path = extract_zip(
            zip_path,
            config.EXTRACT_FOLDER
        )



        # 2. Detectare folder HTML

        html_folder = find_html_folder(
            extract_path
        )



        # 3. Analiză structură

        analysis = analyze_extracted_folder(
            extract_path
        )



        # 4. Grupare articole

        articles = []


        if html_folder:

            articles = detect_articles(
                html_folder
            )



        return render_template(
            "upload.html",

            uploaded=True,

            filename=filename,

            analysis=analysis,

            articles=articles

        )



    return render_template("upload.html")





@app.errorhandler(404)
def page_not_found(error):

    return render_template("404.html"),404





if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
