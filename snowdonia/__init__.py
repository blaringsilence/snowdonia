"""
API
===

For the purposes of this API, we decided to skip the hassle of registering, so if
this is the first time you're using this API, the app will register new vehicles
on the fly. Just send the data and you're golden.

To send data from a vehicle, point to the following link:

    **/api/v1/emissions/<VEHICLE_UUID>**

Where the vehicle UUID is a valid UUID4.

The request should be of type POST, and the data that are expected by the API are:

- **latitude**: floating point between -90 and 90
- **longitude**: floating point between -180 and 180
- **type**: the vehicle's type. Allowed types: taxi, tram, train, and bus.
- **timestamp**: a string in the following format: DD-MM-YYYY hh:mm:ss
- **heading**: an angle between 0 (True North) and 359 that indicates where the vehicle's heading.

Please note that this API is only for public vehicles in Snowdonia, so any co-ordinates outside of 
Snowdonia's 50km radius will yield an error. See snowdonia.register_emission(vehicleID) below for details.

"""
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from math import radians, sqrt, sin, cos, atan, tan, pi, atan2
import re
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

valid_types = ['taxi', 'bus', 'tram', 'train']
"""Valid types of vehicles in Snowdonia."""
snowdonia_center = (radians(53.068889), radians(-4.075556))
"""(lat, long) radian co-ordinates for the town center. Fun fact: This points
to the Snowdonia region in Wales."""

class Vehicle(db.Model):
    """Database model for vehicles. Contains:

    - id (str, UUID4)
    - type (str): taxi, tram, bus, or train
    """
    __tablename__ = 'vehicles'
    id = db.Column(db.String(32), primary_key=True)
    type = db.Column(db.String)
    emissions = db.relationship('Emission', backref='vehicle', lazy='dynamic')

    def __init__(self, id, type):
        self.id = id
        self.type = type

class Emission(db.Model):
    """Database model for emissions. Contains:
    
    - id (int, auto-incremented)
    - vehicle_id (foreign key referencing the UUID in vehicles)
    - latitude (float from -90 to 90)
    - longitude (float from -180 to 180)
    - timestamp (DateTime)
    - heading (int, angle, from 0 - True North - to 359)
    """
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
    """Checks:
    
    - Vehicle ID is a valid UUID4
    - Vehicle type is a valid type (train, tram, taxi, or bus)
    """
    uuid4hex = re.compile('[0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15}\Z', re.I)
    match = uuid4hex.match(vID)
    return match is not None and vType in valid_types

def valid_point(lat_val, long_val, heading):
    """Checks:

    - Latitude is between -90 and 90
    - Longitude is between -180 and 180
    - Heading is between 0 and 359
    - Point is within the town borders (less than 50km from town center)
    """
    lat_valid = lat_val >= -90 and lat_val <= 90
    long_valid = long_val >= -180 and long_val<= 180
    heading_valid = heading >= 0 and heading <= 359
    in_city = in_range(lat_val, long_val) if lat_valid and long_valid else False
    return in_city and heading_valid


def distance_from_center(latitude, longitude): 
    """Calculates the distance between the provided point and the town center
    by using Vincenty's formula that calculates the distance between
    two points on a spheroid, given:

    - Radius of the Earth (min and max) as well as its flattening.
    - Latitude and longitude of both the point & the center in radians.

    Even though there exists the Haversine formula that calculates the distance
    between two points on a sphere, and it is less computationally expensive
    than Vincenty (no iterations), the Haversine formula, when calculating distances
    on the Earth, can have an error up to 0.55%, though generally below 0.3%, 
    so Vincenty provides greater accuracy that is actually needed in this situation,
    where exactly where vehicles were is valuable data.

    More on how Vincenty's formula works:
    https://en.wikipedia.org/wiki/Vincenty's_formulae
    """
    lat_rad, long_rad = radians(latitude), radians(longitude)
    lat_center, long_center = snowdonia_center
    a = 6378137 # earth radius at equator in m
    b = 6356752.3142 # earth smallest radius in m
    f = 1/298.257223563  # flattening of the Earth - all WGS-84 ellipsiod
    L = long_rad - long_center
    U1 = atan((1 - f) * tan(lat_rad))
    U2 = atan((1 - f) * tan(lat_center))
    sin_U1 = sin(U1)
    cos_U1 = cos(U1)
    sin_U2 = sin(U2)
    cos_U2 = cos(U2)
    lambda1 = L
    lambdaP = 2*pi
    iter_limit = 20

    while abs(lambda1 - lambdaP) > 1e-12 and --iter_limit > 0:
        sin_lambda1 = sin(lambda1)
        cos_lambda1 = cos(lambda1)
        sin_sigma = sqrt((cos_U2 * sin_lambda1) * (cos_U2 * sin_lambda1) +\
                    (cos_U1 * sin_U2 - sin_U1 * cos_U2 * cos_lambda1) *\
                    (cos_U1 * sin_U2 - sin_U1 *cos_U2 * cos_lambda1))
        if sin_sigma == 0:
            return 0
        cos_sigma = sin_U1 * sin_U2 + cos_U1 * cos_U2 * cos_lambda1
        sigma = atan2(sin_sigma, cos_sigma)
        sin_alpha = cos_U1 * cos_U2 * sin_lambda1 / sin_sigma
        cos2_alpha = 1 - sin_alpha * sin_alpha
        cos2_sigma_m = cos_sigma - 2 * sin_U1 * sin_U2 / cos2_alpha \
                    if cos2_alpha != 0 else 0
        C = f / 16 * cos2_alpha * (4 + f * (4 - 3 * cos2_alpha))
        lambdaP = lambda1
        lambda1 = L + (1 - C) * f * sin_alpha *\
                (sigma +\
                 C * sin_sigma *\
                 (cos2_sigma_m + C * cos_sigma *\
                 (-1 + 2 * cos2_sigma_m * cos2_sigma_m))\
                )

    if iter_limit==0:
        return None # failed to converge

    u_2 = cos2_alpha * (a * a - b * b) / (b * b)
    A = 1 + u_2 / 16384 *(4096 + u_2 * (-768 + u_2 * (320 - 175 * u_2)))
    B = u_2 / 1024 * (256 + u_2 * (-128 + u_2 * (74 - 47 * u_2)))
    delta_sigma = B * sin_sigma * (cos2_sigma_m + B / 4 *\
                                  (cos_sigma * (-1 + 2 *\
                                   cos2_sigma_m*cos2_sigma_m)-\
                                   B / 6 * cos2_sigma_m *\
                                   (-3 + 4 * sin_sigma * sin_sigma) *\
                                   (-3+4*cos2_sigma_m*cos2_sigma_m))\
                                  )
    s = b*A*(sigma-delta_sigma)
    return s/1000


def in_range(latitude, longitude):
    """Determins if distance from center is <= 50, Snowdonia's radius in kms."""
    return distance_from_center(latitude, longitude) <= 50

@app.route('/')
def home():
    """A brief summary page and the landing page for the app."""
    return render_template('about.html')

@app.route('/api/v1/emission/<vehicleID>', methods=['POST'])
def register_emission(vehicleID): 
    """The API endpoint that collects emissions.
    URL:
    ::
        /api/v1/emission/<VEHICLE_ID>

    How it works:

    - The UUID4 for the vehicle is provided in the API endpoint URL
    - The data that have to accompany the POST request:
        - latitude: float between -90 and 90
        - longitude: float betwen -180 and 180
        - timestamp: string of the timestamp in the form: DD-MM-YYYY hh:mm:ss
        - heading: int from 0 to 359

    Responses:

    - Success [200]: 'Success!'
    - Co-ordinates or heading invalid/Co-ordinates are too far [400]: 'Co-ordinates/heading invalid'
    - Vehicle ID or vehicle type invalid [400]: 'Vehicle ID or vehicle type is invalid'
    - Invalid data types [400]: 'Invalid value(s) provided'
    - Other exception [400]: 'Unexpected error'
    """
    try:
        # 1. Validate
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        timestamp = datetime.strptime(request.form['timestamp'],\
                    '%d-%m-%Y %H:%M:%S')
        heading = int(request.form['heading'])
        if not valid_point(latitude, longitude, heading):
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
    except Exception:
        return 'Error! Did you send the right data fields?', 400
    return 'Success!', 200


@app.route('/loaderio-84b80b047916decb9c20501064268c92/')
def loader():
    return 'loaderio-84b80b047916decb9c20501064268c92'