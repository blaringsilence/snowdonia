from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
from sqlalchemy.exc import IntegrityError
from math import radians, asin, sqrt, sin, cos

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
valid_types = ['taxi', 'bus', 'tram', 'train']
snowdonia_center = (radians(53.068889), radians(-4.075556)) # (lat, long)

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.String(32), primary_key=True)
    type = db.Column(db.String)
    emissions = db.relationship('Emission', backref='vehicle', lazy='dynamic')

    def __init__(self, id, type):
        self.id = id
        self.type = type

class Emission(db.Model):
    __tablename__ = 'emissions'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.String(32), db.ForeignKey('vehicles.id'))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    timestamp = db.Column(db.DateTime)
    heading = db.Column(db.Integer)

    def __init__(self, vehicle_id, latitude, longitude, timestamp, heading):
        self.vehicle_id = vehicle_id
        self.latitude = latitude
        self.longitude = longitude
        self.timestamp = timestamp
        self.heading = heading

def valid_vehicle(vID, vType):
    uuid4hex = re.compile('[0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15}\Z', re.I)
    match = uuid4hex.match(vID)
    return match is not None and vType in valid_types


def valid_point(latitude, longitude, heading):
    lat_valid = latitude >= -90 and latitude <= 90
    long_valid = longitude >= -180 and longitude <= 180
    heading_valid = heading >= 0 and heading <= 359
    return lat_valid and long_valid and heading_valid

def distance_from_center(latitude, longitude): # Haversine formula
    earth_radius = 6371 # kms
    lat_rad, long_rad = radians(latitude), radians(longitude)
    lat_center, long_center = snowdonia_center
    a = (lat_rad - lat_center) / 2
    b = (long_rad - long_center) / 2
    distance = 2 * earth_radius *\
               asin(\
                sqrt(pow(sin(a), 2)\
                + cos(lat_rad) * cos(lat_center) * pow(sin(b),2))\
                )
    return distance

def in_range(latitude, longitude):
    # Ignores the (max) 0.5% possible error by the Haversine formula due
    # to the earth being a spheroid
    return distance_from_center(latitude, longitude) <= 50

@app.route('/')
def home():
    return 'Snowdonia!'

@app.route('/api/v1/emission/<vehicleID>', methods=['POST'])
def register_emission(vehicleID): 
    try:
        # 1. Validate
        latitude, longitude = float(request.form['latitude']), float(request.form['longitude'])
        timestamp = datetime.strptime(request.form['timestamp'], '%d-%m-%Y %H:%M:%S')
        heading = int(request.form['heading'])
        if not valid_point(latitude, longitude, heading) or not in_range(latitude, longitude):
            return 'Co-ordinates/heading invalid.', 400
        # 2. Register vehicle if not registered
        record = Vehicle.query.filter_by(id=vehicleID).first()
        if record is None:
            vehicle_type = request.form['type'].lower()
            if not valid_vehicle(vehicleID, vehicle_type):
                return 'Vehicle ID or vehicle type is invalid.', 400
            vehicle = Vehicle(vehicleID, vehicle_type)
            db.session.add(vehicle)
            db.session.commit()
        # 3. Register emission
        emission = Emission(vehicleID, latitude, longitude, timestamp, heading)
        db.session.add(emission)
        db.session.commit()
    except ValueError:
        return 'Invalid value(s) provided.', 400
    return 'Success!', 200


