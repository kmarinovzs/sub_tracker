from flask import Blueprint, jsonify, render_template, redirect, flash, session, request, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Subscription

app_bp = Blueprint('main', __name__, template_folder="templates")
        


@app_bp.route("/", methods=["GET"])
def index():
    return render_template("layout.html")


@app_bp.route("/register", methods=["GET", "POST"])
def register(): 
    if request.method == "POST":
        username = request.form.get("username")

        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            flash("Fill all the fields")
            return redirect(url_for("main.register"))
        
        if password != confirmation:
            flash("Passwords do not match")
            return redirect(url_for("main.register"))
        
        user = User(username=username, hash=generate_password_hash(password))
        try:
            db.session.add(user)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            db.session.rollback()
            flash("Username may already exist")
            print(f"ERROR: {e}")
            return redirect(url_for("main.register"))
    
    return render_template("register.html")


@app_bp.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        