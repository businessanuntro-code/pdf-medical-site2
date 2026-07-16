import os
from flask import Flask, render_template, request, redirect, url_for, flash

import config


app = Flask(__name__)

app.secret_key = "pdf-medical-site-secret-key"

app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH


# Creează folderele necesare dacă nu există
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
        and filename.rsplit(".", 1)[1].lower() in config.ALLOWED_EXTENSIONS
    )


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
            flash("Nu a fost selectată nicio arhivă.")
            return redirect(request.url)

        file = request.files["revista"]

        if file.filename == "":
            flash("Nu a fost selectat niciun fișier.")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Este permis doar formatul ZIP.")
            return redirect(request.url)

        filename = file.filename

        save_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(save_path)

        return render_template(
            "upload.html",
            uploaded=True,
            filename=filename
        )

    return render_template("upload.html")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
