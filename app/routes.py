from flask import Blueprint, jsonify, render_template, redirect, flash, session, request, flash, url_for
from functools import wraps
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Subscription, db
from sqlalchemy import func

app_bp = Blueprint('main', __name__, template_folder="templates")
        
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("main.login"))
        return f(*args, **kwargs)
    return decorated_function

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
            session["logged_in"] = True     
            return redirect(url_for("main.dashboard"))
        else:
            flash("Username or password are not correct")
            return redirect(url_for("main.login"))
    print(session)
    return render_template("login.html")
            

@app_bp.route("/logout")
@login_required
def logout():

    session.clear()
    print(session)
    return redirect(url_for("main.index"))


@app_bp.route("/add", methods=["GET" ,"POST"])
@login_required
def add():
    if request.method == "POST":
        name = request.form.get("subscription")
        billing = request.form.get("billing")
        amount = request.form.get("amount")

        if not name or not billing or not amount:
            flash("Fill all the fields correctly")
            return redirect(url_for("main.add"))
        user = session["user_id"]

        next_due_date = datetime.now() + relativedelta(months=1) if billing == "monthly" else datetime.now() + relativedelta(years=1)

        subscription = Subscription(user_id=user, name=name, billing_cycle=billing, amount=amount, next_due_date=next_due_date)
        try:
            db.session.add(subscription)
            db.session.commit()
            return redirect(url_for("main.dashboard"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while adding the subscription")
            print(f"ERROR: {e}")
            return redirect(url_for("main.add"))

    return render_template("add.html")


@app_bp.route("/delete/<int:subscription_id>", methods=["POST"])
@login_required
def delete(subscription_id):
    subscription = Subscription.query.filter_by(id=subscription_id).first()

    try:
        db.session.delete(subscription)
        db.session.commit()
        return redirect(url_for("main.dashboard"))
    except Exception as e:
        db.session.rollback()
        flash("An error occured while trying to delete the subscription")
        print(f"ERROR: {e}")
        return redirect(url_for("main.dashboard"))


@app_bp.route("/dashboard")
@login_required
def dashboard():

    subscriptions = Subscription.query.filter_by(user_id=session["user_id"]).all()
    active_subs = Subscription.query.filter_by(user_id=session["user_id"]).count()
    sum_monthly = sum(sub.amount for sub in subscriptions if sub.billing_cycle == "monthly")
    sum_yearly = sum(sub.amount for sub in subscriptions if sub.billing_cycle == "yearly")
    sum_monthly += sum_yearly / 12
    total_yearly = 12 * sum_monthly
    
    return render_template("dashboard.html", subscriptions=subscriptions, active_subscriptions=active_subs, average_monthly=sum_monthly, total_yearly=total_yearly)    


@app_bp.route("/chart-data")
def chart_data():

    data = Subscription.query.filter_by(user_id=session["user_id"]).all()

    ls = []
    for d in data:
        if d.billing_cycle == "monthly":
            ls.append(d.amount)
        else:
            ls.append(round(d.amount / 12, 2))

    return jsonify({
        "labels": [d.name for d in data],
        "values": ls
    }) 


@app_bp.route("/demo")
def demo():

    return 
