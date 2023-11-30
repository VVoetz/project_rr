import os

from flask import Flask, render_template, session, jsonify, request, flash, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

from models import *
from helpers import login_required

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db.init_app(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


    
@app.route("/start", methods=["GET", "POST"])
@login_required
def index():

    user = User.query.filter_by(id=str(session["user_id"])).first()
    username = str(user.username)
    markers = Markers.query.filter_by(placedby=username).all()
    rendermap = True
    return render_template("start.html", markers = markers, rendermap = rendermap)

@app.route("/addtest", methods=["GET", "POST"])
@login_required
def addtest():

    flash("testttest")
    return redirect("/start")

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.form.get("lat") == "":
        flash("No location selected")
        return redirect("/start")
     
    markerlat = request.form.get("lat")
    markerlng = request.form.get("lng")
    if not request.form.get("name"):
        flash("no name given")
        return redirect("/start")
    marker = Markers()
    marker.horizontal = markerlat
    marker.vertical = markerlng
    
    
    user = User.query.filter_by(id=str(session["user_id"])).first()
    username = str(user.username)
    
    marker.placedby = username
    marker.name = request.form.get("name")
    db.session.add(marker)
    db.session.commit()
    flash(username)
    return redirect("/start")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        
        if not username:
            flash("no username given")
            return redirect("/register")
        if not password:
            flash("no password given")
            return render_template("register.html")
        if not confirmation:
            flash("no confirmation given")
            return render_template("register.html")
        if password != confirmation:
            flash("passwords don't match")
            return render_template("register.html")
            
        hashed_password = generate_password_hash(password)
        usercheck = User.query.filter_by(username=str(username)).first()
        
        if usercheck != None:
            flash(f"{usercheck.username} already in database")
            return render_template("register.html")
        user = User(username=str(username), password=str(hashed_password))
        db.session.add(user)
        db.session.commit()
    return redirect("/login")
    
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        session.clear()
        return render_template("login.html")
    else:
    # Forget any user_id
        session.clear()
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("no username given")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("no password given")
            return render_template("login.html")

        # Query database for username
        user = User.query.filter_by(username=str(username)).first()
        
        if user == None:
            flash("username not in database")
            return render_template("login.html")
        
        if user.username != username or not check_password_hash(user.password, password):
            flash("incorrect username/password combination")
            return render_template("login.html")
       

        # Remember which user has logged in
        session["user_id"] = user.id

        # Redirect user to home page
        return redirect("/start")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/start")


if __name__ == '__main__':
    
    app.run(debug=True) 