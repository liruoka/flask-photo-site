from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from config import Config
from forms import UploadForm, LoginForm
from models import db, Photo
import os
from werkzeug.utils import secure_filename, safe_join
from PIL import Image

app = Flask(__name__, static_folder="uploads", static_url_path="/uploads")
app.config.from_object(Config)
Config.init_app(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

with app.app_context():
    db.create_all()

class User(UserMixin):
    id = 1  

@login_manager.user_loader
def load_user(user_id):
    return User() if user_id == "1" else None

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

def compress_image(filepath):
    try:
        img = Image.open(filepath)
        img = img.convert("RGB")
        img.thumbnail((800, 800))
        img.save(filepath, "JPEG", quality=85)
    except Exception as e:
        print(f"Fehler beim Komprimieren des Bildes: {e}")

@app.route("/", methods=["GET", "POST"])
def upload_file():
    form = UploadForm()
    if current_user.is_authenticated and form.validate_on_submit():
        files = form.files.data
        uploaded_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.abspath(os.path.join(app.config["UPLOAD_FOLDER"], filename))  # Абсолютный путь
                file.save(filepath)
                compress_image(filepath)
                new_photo = Photo(filename=filename)
                db.session.add(new_photo)
                uploaded_files.append(filename)
        db.session.commit()
        flash(f"{len(uploaded_files)} Datei(en) hochgeladen!", "success")
        return redirect(url_for("upload_file"))

    photos = Photo.query.all()
    return render_template("index.html", form=form, photos=photos)

@app.route("/download/<filename>")
def download_file(filename):
    upload_folder_abs = os.path.abspath(app.config["UPLOAD_FOLDER"])  # Абсолютный путь к папке uploads
    file_path = safe_join(upload_folder_abs, filename)
    
    if not os.path.exists(file_path):
        abort(404, description="Datei nicht gefunden")

    return send_from_directory(upload_folder_abs, filename, as_attachment=True)

@app.route("/delete/<int:photo_id>", methods=["POST"])
@login_required
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    upload_folder_abs = os.path.abspath(app.config["UPLOAD_FOLDER"])
    filepath = safe_join(upload_folder_abs, photo.filename)
    
    if os.path.exists(filepath):
        os.remove(filepath)

    db.session.delete(photo)
    db.session.commit()
    flash("Foto wurde gelöscht!", "success")
    return redirect(url_for("upload_file"))

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == app.config["ADMIN_USERNAME"] and form.password.data == app.config["ADMIN_PASSWORD"]:
            user = User()
            login_user(user)
            return redirect(url_for("upload_file"))
        flash("Falsche Anmeldeinformationen", "danger")
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("upload_file"))

if __name__ == "__main__":
    port=int(os.environ.get("PORT",8080))
    app.run(host="0.0.0.0:8080",port=port)