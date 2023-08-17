from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    vehicles = db.relationship('Vehicle', backref='owner', lazy=True) 

class ParkingSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    slot_number = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=True, unique=True) 

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    license_plate = db.Column(db.Integer, unique=True)
    status = db.Column(db.String(10), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    

    
