.. Snowdonia documentation master file, created by
   sphinx-quickstart on Wed Nov 23 23:50:46 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Snowdonia - Transport API
=========================

.. toctree::
   :maxdepth: 2

.. _intro:

Introduction
------------
About
~~~~~
This API was mainly built to provide an endpoint to collect emissions containing location and path data from different public transportation vehicles around Snowdonia. Emissions are sent every 20 seconds from nearly 1000 vehicles.

Docs below include documentation for the available endpoints and unit tests.

`Logo Credit`_.

Installation
~~~~~~~~~~~~
1. Clone the github repo
::
	$ git clone https://github.com/blaringsilence/snowdonia.git
	$ cd snowdonia

2. Install virtualenv and activate it
::
	$ pip install virtualenv
	$ virtualenv --python=3.4 venv
	$ . venv/bin/activate

3. Install requirements
::
	$ pip install -r requirements.txt

4. Install postgresql (see `download page`_) and create a user and a database
::
	$ sudo -u postgres createuser -s $USER
	$ createdb -U $USER snowdonia

5. Edit the config.py file in the (second) snowdonia dir (replace USER and PASSWORD with your postgresql user and password)

6. Create the database tables. In a python interpreter:
::
	>> from snowdonia import db
	>> db.create_all()

7. Run the app using gunicorn (replace 6 with the suitable number of workers for your testing):
::
	$ gunicorn snowdonia:app -w 6


Testing
-------

Unit Tests
~~~~~~~~~~
Unit tests for the API endpoint (local, postgresql installation/configuration in the app required) are documented below and can be executed as follows:
::
	$ chmod a+x test.py
	$ ./test.py

Stress/Load Tests
~~~~~~~~~~~~~~~~~~
For the purposes of simulating the API's behavior, we're using `Locust`_, an open source load testing tool that uses `gevent`_ to swarm a website with requests whose behavior is described in a local configuration file.

To load the testing tool (while in the virtualenv where the requirements are installed)
::
	$ cd stress_tests
	$ locust

Note that this would run tests on the deployed herokuapp, not locally/on your deployed app. To do that, either change the host in the locustfile, or more easily, add the host parameter:
::
	$ locust --host=[YOUR_HOST_AND_PORT_HERE]

Then head to localhost:8089, and set it to simulate 1000 users with 50 new locusts hatched/second. This should simulate the use of the system the way it's intended to be:

- 1000 concurrent behicles at max
- Emit every 20 seconds
- For each vehicle, a UUID
- For each emission, a location that is within the 50km radius of Snowdonia, a valid type, a valid timestamp, and a valid heading.

Please note that the new points for each vehicle are random so not necessarily in the direction their previous point was supposed to be headed.

In order to see which vehicle is emitting what data, the name of the request (in the Locust web interface) is set to:
::
	TYPE_OF_VEHICLE-INDEX_OF_VEHICLE at (LATITUDE, LONGITUDE)

Where:

- TYPE_OF_VEHICLE is tram, bus, train, or taxi
- INDEX_OF_VEHICLE is the index of this vehicle in relation to others of its kind

For example, the 10th bus' emission at lat=53.1725575782715 and long=-4.3319528534938545:
::
	bus-10 at (53.1725575782715, -4.3319528534938545)


.. _docs:

Docs
----
.. automodule:: snowdonia
	:members:

.. automodule:: test
	:members:




.. _Logo Credit: http://www.flaticon.com/authors/baianat
.. _download page: http://www.postgresql.org/download/
.. _Locust: http://locust.io/
.. _gevent: http://www.gevent.org/

