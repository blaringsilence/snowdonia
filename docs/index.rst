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

5. Create a config.py file in the (second) snowdonia dir with the following (replace USER and PASSWORD with your postgresql user and password)
::
	SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://USER:PASSWORD@localhost/snowdonia'
	SQLALCHEMY_TRACK_MODIFICATIONS = False

6. Create the database tables. In a python interpreter:
::
	>> from snowdonia import db
	>> db.create_all()

7. Run the app. In a python interpreter:
::
	>> from snowdonia import app
	>> app.run()
	
.. _docs:

Docs
----
.. automodule:: snowdonia
	:members:

.. automodule:: test
	:members:




.. _Logo Credit: http://www.flaticon.com/authors/baianat
.. _download page: http://www.postgresql.org/download/

