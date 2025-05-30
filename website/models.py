from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask import Flask
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime

db = SQLAlchemy() #initial DB

#user model

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique = True, nullable = False)
    email = db.Column(db.String(100), unique = True, nullable = False)
    password_hash = db.Column(db.String(128), nullable = False)
    role = db.Column(db.String(20), nullable = False, default = "general")
    Parking_lots = db.relationship('Parking_lot', backref = 'user', lazy = True)
    vehicle_no = db.Column(db.String(20), nullable = True)
    bookings = db.relationship('Booking', backref='user', lazy=True)
    spot_statuses = db.relationship('Spot_status', backref='user', lazy=True)
    
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'

class Parking_lot(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    prime_location = db.Column(db.String(200), nullable = False)
    address = db.Column(db.String(200), nullable = False)
    price_per_hour = db.Column(db.Float, nullable = False)
    max_no_spots = db.Column(db.Integer, nullable = False)
    #created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) 
    spots = db.relationship('Parking_spot', backref='lot', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f'<ParkingLot {self.name}>'    

class Parking_spot(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    parking_lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable = False)
    spot_number = db.Column(db.String(10), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = True)
    vehicle_no = db.Column(db.String(20), nullable = True)
    # Establishing a one-to-many relationship with Booking  
    bookings = db.relationship('Booking', backref='parking_spot', lazy=True, cascade="all, delete")
    # Establishing a one-to-many relationship with Spot_status
    spot_statuses = db.relationship('Spot_status', backref='parking_spot', lazy=True, cascade="all, delete")
    #is_booked = db.Column(db.Boolean, default = False)
    #is_occupied = db.Column(db.Boolean, default = False)
    #is_available = db.Column(db.Boolean, default = True)
    # Adding a boolean field to indicate availability
    is_available = db.Column(db.Boolean, default = True)
    
    
    def __repr__(self):
        return f'<ParkingSpot {self.spot_number}>'
    
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    Parking_lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable = False)
    parking_spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable = False)
    vehicle_no = db.Column(db.String(20), nullable = False)
    in_time = db.Column(db.DateTime, default=datetime.utcnow)
    #start_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    def __repr__(self):
        return f'<Booking {self.id}>'
   
class Spot_status(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    Parking_lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable = False)
    parking_spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    status = db.Column(db.String(20), nullable = False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SpotStatus {self.id}>'            