from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
import os

app = Flask(__name__)
app.secret_key = "tu_clave_secreta"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Modelo de Usuario
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # "student" o "teacher"

# Modelo para Tareas/Entregas
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    filename = db.Column(db.String(150), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ruta de Inicio
@app.route("/")
def index():
    return render_template("base.html")

# Ruta para Registro
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("El usuario ya existe.")
            return redirect(url_for("register"))
        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash("Registro exitoso. Inicia sesión.")
        return redirect(url_for("login"))
    return render_template("register.html")

# Ruta para Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Usuario o contraseña incorrectos.")
    return render_template("login.html")

# Ruta para el Panel de Usuario
@app.route("/dashboard")
@login_required
def dashboard():
    submissions = Submission.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", user=current_user, submissions=submissions)

# Ruta para Subir Archivos
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        file = request.files["file"]
        filename = file.filename
        file.save(f"static/uploads/{filename}")
        new_submission = Submission(
            title=title, description=description, filename=filename, user_id=current_user.id
        )
        db.session.add(new_submission)
        db.session.commit()
        flash("Subida exitosa.")
        return redirect(url_for("dashboard"))
    return render_template("upload.html")

# Ruta para Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# Configuración para Render (Puerto dinámico)
if __name__ == "__main__":
    # Render requiere vincular al puerto que asigna dinámicamente
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
