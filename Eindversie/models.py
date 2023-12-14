from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Markers(db.Model):
    __tablename__ = "markers"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    horizontal = db.Column(db.String, nullable=False)
    vertical = db.Column(db.String, nullable=False)
    placedby = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

class Friends(db.Model):
    __tablename__ = "friends"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    friend = db.Column(db.String, nullable=False)
    friend_id = db.Column(db.Integer, nullable=False)

class Requests(db.Model):
    __tablename__ = "requests"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    friend = db.Column(db.String, nullable=False)
    friend_id = db.Column(db.Integer, nullable=False)  