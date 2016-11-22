from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

class Vehicle(db.Model):
	__tablename__ = 'vehicles'
	id = db.Column(db.String(32), primary_key=True)
	type = db.Column(db.String) # limit this
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

@app.route('/')
def home():
	return 'hello world'

if __name__ == '__main__':
	app.run()
