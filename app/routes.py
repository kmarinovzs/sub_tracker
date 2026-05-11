from flask import Blueprint, jsonify, render_template, redirect, flash, session, request, flash, url_for
from functools import wraps
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Subscription, db
from sqlalchemy import func

app_bp = Blueprint('main', __name__, template_folder="templates")


def check_date(next_due_date):
    today = datetime.now()

    if today.month == 12:
        month = 1
    else:
        month = today.month + 1
    
    return next_due_date.month == month


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

    flash("Fill all the fields correctly and try again")
    return redirect(url_for("main.dashboard"))


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


@app_bp.route("/edit/<int:subscription_id>", methods=["POST"])
@login_required
def edit(subscription_id):
    sub = Subscription.query.get_or_404(subscription_id)

    name = request.form.get("subscription")
    amount = request.form.get("amount")
    billing = request.form.get("billing")

    if not name or not amount or not billing:
        flash("Enter all data correctly")
        return redirect(url_for("main.dashboard"))
    
    sub.name = name 
    sub.amount = amount
    sub.billing_cycle = billing
    try:
        db.session.commit()
        return redirect(url_for("main.dashboard"))
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: {e}")
        flash("Edit was not possible, try again later")
        return redirect(url_for("main.dashboard"))


@app_bp.route("/dashboard")
@login_required
def dashboard():
    update_dates()

    subscriptions = Subscription.query.filter_by(user_id=session["user_id"]).all()
    active_subs = Subscription.query.filter_by(user_id=session["user_id"]).count()
    sum_monthly = sum(sub.amount for sub in subscriptions if sub.billing_cycle == "monthly")
    sum_yearly = sum(sub.amount for sub in subscriptions if sub.billing_cycle == "yearly")
    sum_monthly += sum_yearly / 12
    total_yearly = 12 * sum_monthly
    due_next_month = 0

    for sub in subscriptions:
        if check_date(sub.next_due_date):
            due_next_month += sub.amount
        
    cheapest_sub_m = Subscription.query.filter_by(user_id=session["user_id"]).filter_by(billing_cycle="monthly").order_by(Subscription.amount.asc()).first()
    cheapest_sub_y = Subscription.query.filter_by(user_id=session["user_id"]).filter_by(billing_cycle="yearly").order_by(Subscription.amount.asc()).first()
    
    if cheapest_sub_m and cheapest_sub_y:
        if cheapest_sub_m.amount < cheapest_sub_y.amount / 12:
            lowest_expense = cheapest_sub_m.name
        else:
            lowest_expense = cheapest_sub_y.name
    elif cheapest_sub_m and not cheapest_sub_y:
        lowest_expense = cheapest_sub_m.name
    elif cheapest_sub_y and not cheapest_sub_m:
        lowest_expense = cheapest_sub_y.name
    else:
        lowest_expense = ""

    highest_sub_m = Subscription.query.filter_by(user_id=session["user_id"]).filter_by(billing_cycle="monthly").order_by(Subscription.amount.desc()).first()
    highest_sub_y = Subscription.query.filter_by(user_id=session["user_id"]).filter_by(billing_cycle="yearly").order_by(Subscription.amount.desc()).first()

    if highest_sub_m and highest_sub_y:
        if highest_sub_m.amount > highest_sub_y.amount / 12:
            highest_expense = highest_sub_m.name
        else:
            highest_expense = highest_sub_y.name
    elif highest_sub_m and not highest_sub_y:
        highest_expense = highest_sub_m.name
    elif highest_sub_y and not highest_sub_m:
        highest_expense = highest_sub_y.name
    else:
        highest_expense = ""
    
    return render_template("dashboard.html", subscriptions=subscriptions, active_subscriptions=active_subs, average_monthly=sum_monthly, total_yearly=total_yearly, due_next_month=due_next_month, lowest_expense=lowest_expense, highest_expense=highest_expense)    


@app_bp.route("/chart-data")
def chart_data():

    data = Subscription.query.filter_by(user_id=session["user_id"]).all()

    return jsonify({
        "labels": [d.name for d in data],
        "values": [d.amount if d.billing_cycle == "monthly" else round(d.amount / 12, 2) for d in data]
    })


@app_bp.route("/demo")
def demo():

    user = User.query.filter_by(username="DemoUser").first()

    if not user:
        try:
            user = User(username="DemoUser", hash=generate_password_hash("DemoPassword"))
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: {e}")
            flash("Demo Version is not working")

    seed_demo()

    session["user_id"] = user.id
    session["username"] = user.username
    session["logged_in"] = True
    return redirect(url_for("main.dashboard"))


def seed_demo():
    user = User.query.filter_by(username="DemoUser").first()

    Subscription.query.filter_by(user_id=user.id).delete()

    next_due_date_m = datetime.now() + relativedelta(months=1)
    next_due_date_y = datetime.now() + relativedelta(years=1)

    subs = [Subscription(user_id=user.id, name="Netflix", amount=7.99, billing_cycle="monthly", next_due_date=next_due_date_m),
            Subscription(user_id=user.id, name="Amazon Prime", amount=45.99, billing_cycle="yearly", next_due_date=next_due_date_y),
            Subscription(user_id=user.id, name="Disney+", amount=12.99, billing_cycle="monthly", next_due_date=next_due_date_m),
            Subscription(user_id=user.id, name="YouTube Premium", amount=15.99, billing_cycle="monthly", next_due_date=next_due_date_m)]
    
    try:
        db.session.add_all(subs)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")


def update_dates():
    now = datetime.now()
    subs = Subscription.query.filter(Subscription.next_due_date < now).all()

    for sub in subs:
        if sub.billing_cycle == "monthly":
            sub.next_due_date += relativedelta(months=1)
        else:
            sub.next_due_date += relativedelta(years=1)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: {e}")