from flask import Blueprint, jsonify, render_template, redirect, flash, session, request, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Subscription, db

app_bp = Blueprint('main', __name__, template_folder="templates")
        

@app_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


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
            flash("The username already exists")
            print(f"ERROR: {e}")
            return redirect(url_for("main.register"))
    
    return render_template("register.html")


@app_bp.route("/login", methods = ["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Enter your username and password correctly!")
            return redirect(url_for("main.login"))
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.hash, password):
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("main.index"))
        else:
            flash("Username or password are not correct")
            return redirect(url_for("main.login"))
        
    return render_template("login.html")
            

@app_bp.route("/logout", methods = ["POST"])
def logout():

    session.clear()
    return redirect(url_for("main.index"))

