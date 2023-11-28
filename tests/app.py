import os

from flask import Flask, render_template, session, jsonify, request, flash, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
    
from models import *

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


class Marker:
    def __init__(self, long, wide):
        self.horizontal = long
        self.vertical = wide
        
@app.route("/start", methods=["GET", "POST"])
def index():

    markers = Markers.query.all()
    
    return render_template("start.html", markers = markers)

@app.route("/addtest", methods=["GET", "POST"])
def addtest():

    marker = Markers()
    marker.horizontal = str(52.354596)
    marker.vertical = str(4.954384)
    marker.placedby = "ikke"
    marker.name = "London_test"
    db.session.add(marker)
    db.session.commit()
    return redirect("/start")

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.form.get("lat") == "":
        flash("No location selected")
        return redirect("/start")
     
    markerlat = request.form.get("lat")
    markerlng = request.form.get("lng")
    flash(markerlat + markerlng)
    marker = Markers()
    marker.horizontal = markerlat
    marker.vertical = markerlng
    marker.placedby = "ikke"
    marker.name = "test"
    db.session.add(marker)
    db.session.commit()
    return redirect("/start")

if __name__ == '__main__':
    
    app.run(debug=True) 