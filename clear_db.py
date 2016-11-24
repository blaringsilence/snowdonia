#!/usr/bin/env python
from snowdonia import *

db.session.query(Emission).delete()
db.session.query(Vehicle).delete()
db.session.commit()