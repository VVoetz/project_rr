from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Markers(db.Model):
    __tablename__ = "markers"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    horizontal = db.Column(db.String, nullable=False)
    vertical = db.Column(db.String, nullable=False)
    placedby = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)