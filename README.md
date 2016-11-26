# Snowdonia Transport API
[![Documentation Status](https://readthedocs.org/projects/snowdonia/badge/?version=latest)](http://snowdonia.readthedocs.io/en/latest/?badge=latest)  [![Heroku](http://heroku-badge.herokuapp.com/?app=snowdonia-transport&style=flat)](http://snowdonia-transport.herokuapp.com)

An API that was mainly built to provide an endpoint to collect emissions containing location and path data from different public transportation vehicles around Snowdonia, per this [challenge](CHALLENGE.md). Emissions are sent every 20 seconds from nearly 1000 vehicles.

This readme offers a quickstart to installing/running the app as well as a guide to the endpoint request format. For the full documentation covering all the code and tests, **[read the docs here](http://snowdonia.readthedocs.io/en/latest/).**

To see/use the app right now, it's **deployed on [Heroku](http://snowdonia-transport.herokuapp.com).**

**For the required load testing results and instructions on how to test, see the [readme](stress_tests/README.md) under [stress_tests](stress_tests).**

## Install
1. Clone the repo.

  ```bash
    $ git clone https://github.com/blaringsilence/snowdonia.git
    $ cd snowdonia
  ```
2. Install virtualenv if not already on your machine and activate it in this project.

  ```bash
    $ pip install virtualenv
    $ virtualenv --python=3.4 venv
    $ . venv/bin/activate
  ```
(to deactivate the virtualenv, just run `$ deactivate`)

3. Install requirements/dependencies.

  ```bash
    $ pip install -r requirements.txt
  ```
4. [Install postgresql](http://www.postgresql.org/download/) if not already installed, then create a new user (replace $USER with your username) and a database:

  ```bash
    $ sudo -u postgres createuser -s $USER 
    $ createdb -U $USER snowdonia
  ```
5. Edit [config.py](snowdonia/config.py) and replace USER:PASSWORD with your database username and password.
6. Create the database tables. In a python interpreter:

  ```python
    >> from snowdonia import db
    >> db.create_all()
  ```
Now, you're all set. Whenever you want, you can run the app with gunicorn (replace 6 with the number of workers needed for your testing/dev purposes):

  ```bash
    $ gunicorn snowdonia:app -w 6
  ```

## Use the API endpoint
The endpoint can be found at `/api/v1/emission/<VEHICLE_UUID>` where `<VEHICLE_UUID>` is the UUID4 of the vehicle. For the purposes of this challenge, this one endpoint serves to both register a vehicle if it's its first request and keep records of the emissions. This is impractical (and exposes the API to fake data) in a real-life scenario, though.

The request is of type **PUT** and the data that the endpoints expects is:
```javascript
  {
    'latitude': //float between -90 and 90,
    'longitude': //float between -180 and 180,
    'type': //string type of the vehicle. Must be a valid type: train, tram, taxi, or bus,
    'heading': //angle from 0 (True North) to 359 to indicate where the vehicle is headed,
    'timestamp': //string in the form of DD-MM-YYYY hh:mm:ss
  }
```

The API will respond with status code 400 and an error message if:
- Any value does not pass its type/format check
- Latitude and longitude form a point that is more than 50km away from Snowdonia's center
- It doesn't receive all the data it expects
- An unexpected error occurs
