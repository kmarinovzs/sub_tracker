from flask import Blueprint, jsonify, render_template, redirect, flash, session, request, flash 
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Subscription

main_bp = Blueprint('main', __name__, template_folder="templates")
        


@main_bp.route("/", methods=["GET"])
def index():
    return render_template("layout.html")


@main_bp.route("/register", methods=["GET", "POST"])
def register(): 
    if request.method == "GET":
        return render_template("register.html")
    if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
        flash("You must fill all of the lines correctly")
        return redirect("/register")


@main_bp.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")