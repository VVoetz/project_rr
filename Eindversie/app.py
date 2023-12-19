import os, time

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

@app.route("/")
def begin():
    return redirect("/home")

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():

    # Get information from SQL database to present on map 
    
    user = User.query.filter_by(id=str(session["user_id"])).first()
    username = str(user.username)
    markers = Markers.query.filter_by(placedby=username).all()
    
    # Makes a list of markers from all friends of current user
    friendmarkers = list()
    friendships = Friends.query.filter_by(user_id=session["user_id"]).all()
    for friend in friendships:
        f_markers = Markers.query.filter_by(placedby=friend.friend).all()
        for marker in f_markers:
            friendmarkers.append(marker)
        
    return render_template("home.html", 
                            markers = markers,
                            rendermap = True,
                            fmarkers = friendmarkers,
                            friends = friendships)
    
    
@app.route("/start", methods=["GET", "POST"])
@login_required
def index():
    
    # Get information from SQL database to present on map
    
    user = User.query.filter_by(id=str(session["user_id"])).first()
    username = str(user.username)
    markers = Markers.query.filter_by(placedby=username).all()
    
    # Makes a list of markers from all friends of current user
    
    friendmarkers = list()
    friendships = Friends.query.filter_by(user_id=session["user_id"]).all()
    for friend in friendships:
        f_markers = Markers.query.filter_by(placedby=friend.friend).all()
        for marker in f_markers:
            friendmarkers.append(marker)

    return render_template("start.html",
                           markers = markers,
                           rendermap = True,
                           fmarkers = friendmarkers,
                           friends = friendships,
                           add = True)

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():

    if request.form.get("lat") == "":
        flash("No location selected")
        return redirect("/start")
    
    if not request.form.get("name"):
        flash("no name given")
        return redirect("/start")

    if not request.form.get("description"):
        flash("no description given")
        return redirect("/start")
   
    markerlat = request.form.get("lat")
    markerlng = request.form.get("lng")   
    description = request.form.get("description")
    user = User.query.filter_by(id=str(session["user_id"])).first()
    username = str(user.username)

    marker = Markers()
    marker.horizontal = markerlat
    marker.vertical = markerlng
    marker.placedby = username
    marker.name = request.form.get("name")
    marker.description = description

    db.session.add(marker)
    db.session.commit()

    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        
        # Retrieve information form webpage
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        
        # Checking for errors in registration
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
            
        usercheck = User.query.filter_by(username=str(username)).first()
        if usercheck != None:
            flash(f"{usercheck.username} already in database")
            return render_template("register.html")
        
        # Adding user to database
        hashed_password = generate_password_hash(password)
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
        session["username"] = user.username

        # Redirect user to home page
        return redirect("/")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/restaurant/<int:id>")
def restaurant(id):
    # Check which restaurant needs to be displayed
    markers = Markers.query.filter_by(id=id).first()
    
    # Checks if current user has placed said restaurant
    you = False
    other = False
    if markers.placedby == session["username"]:
        you = True
    else:
        other = True
    
    # Retrieving information of user who placed restaurant
    user = User.query.filter_by(id=str(session["user_id"])).first()
    
    return render_template("restaurant.html",
                            restaurant = markers,
                            you = you,
                            other = other,
                            user = user)

@app.route("/friends")
@login_required
def friends():
    
    # Retrieving information about friendships and requests to present to user
    
    friends = Friends.query.filter_by(user_id=session["user_id"]).all()
    inc_requests = Requests.query.filter_by(friend_id=session["user_id"]).all()
    out_requests = Requests.query.filter_by(user_id=session["user_id"]).all()
    return render_template("friends.html",
                            friends = friends,
                            inc_requests = inc_requests,
                            out_requests = out_requests)

@app.route("/addfriend", methods=["POST"])
@login_required
def add_friend():
    
    # Running tests to make sure it is a valid request
    
    if not request.form.get("friend_id"):
        flash("no username given")
        return redirect("/friends")
    
    friend = request.form.get("friend_id")
    user = User.query.filter_by(id=(session["user_id"])).first()
    friend_db = User.query.filter_by(username=(friend)).first()
    
    if friend_db == None:
        flash("username not in database")
        return redirect("/friends")
    
    if friend == user.username:
        flash("You cannot add yourself as friend")
        return redirect("/friends")
    
    test_request = Requests.query.filter_by(friend=str(friend), user=user.username).first()
    if test_request != None:
        flash("request already sent")
        return redirect("/friends")
    
    test_request2 = Requests.query.filter_by(user=str(friend), friend=user.username).first()
    if test_request2 != None:
        flash("this user already sent you a request, you can accept it on your right")
        return redirect("/friends")
    
    test_friendship = Friends.query.filter_by(user=str(friend), friend=user.username).first()
    if test_friendship != None:
        flash("You are already friends with this user")
        return redirect("friends")
    
    # Adding request to database
    
    db_entry = Requests()
    db_entry.user = user.username
    db_entry.user_id = user.id
    db_entry.friend = friend_db.username
    db_entry.friend_id = friend_db.id
    
    db.session.add(db_entry)
    db.session.commit()
    
    return redirect("/friends")
    
@app.route("/incfriend", methods=["POST"])
@login_required
def incfriend():
    
    # Retrieving information from webpage and database
    
    friend = request.form.get("friendname")
    choice = request.form.get("choice")
    
    friend_db = User.query.filter_by(username=str(friend)).first()
    user_db = User.query.filter_by(id=str(session["user_id"])).first()
    req = Requests.query.filter_by(friend_id=session["user_id"], user=str(friend)).first()
    
    # Adding friendship to database when user accepted request
    
    if choice == "accept":
       friendship = Friends()
       friendship.user = req.user
       friendship.user_id = req.user_id
       friendship.friend = req.friend
       friendship.friend_id = req.friend_id
       
       revFriendship = Friends()
       revFriendship.user = req.friend
       revFriendship.user_id = req.friend_id
       revFriendship.friend = req.user
       revFriendship.friend_id = req.user_id
       
       db.session.add(friendship)
       db.session.add(revFriendship)
       db.session.commit()
    
    # Deleting request from database regardless of choice accept/deny
    db.session.delete(req)
    db.session.commit()
        
    return redirect("/friends")

@app.route("/cancelreq", methods=["POST"])
@login_required
def cancelreq():
    
    # Retrieving information from webpage and database in order to delete request from database
    
    friend = request.form.get("cancel")
    req = Requests.query.filter_by(user_id=str(session["user_id"]), friend=friend).first()
    db.session.delete(req)
    db.session.commit()
    return redirect("/friends")

@app.route("/delfriend", methods=["POST"])
@login_required
def delfriend():

    # Retrieving information from webpage and database in order to delete friendship from database
    
    friend = request.form.get("user")
    friendship1 = Friends.query.filter_by(user_id=str(session["user_id"]), friend=friend).first()
    friendship2 = Friends.query.filter_by(user=friend, friend_id=str(session["user_id"])).first()
    db.session.delete(friendship1)
    db.session.delete(friendship2)
    db.session.commit()
    return redirect("/friends")

@app.route("/delrestaurant", methods=["POST"])
def delrestaurant():

    # Retrieving information from webpage and database in order to delete marker from database
    restaurant = request.form.get("delrestaurant")
    db_entry = Markers.query.filter_by(id=restaurant).first()
    db.session.delete(db_entry)
    db.session.commit() 
    
    # Waiting to make sure the browser does not reload current iframe before the window is refreshed.
    time.sleep(1)
    return redirect(f"/restaurant/{db_entry.id}")

@app.route("/reload", methods=["GET"])
def reload():   
    return redirect("/")
    
if __name__ == '__main__':  
    
    app.run(debug=True) 