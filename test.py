#!/usr/bin/env python3
import snowdonia
import unittest
import time
import uuid

class TestCase(unittest.TestCase):
	def setUp(self):
		snowdonia.app.config['TESTING'] = True
		self.app = snowdonia.app.test_client()

	def emit(self, vID, type_val, lat_val, long_val, timestamp, heading):
		return self.app.post('/api/v1/emission/' + vID, data=dict(
				type = type_val,
				latitude = lat_val,
				longitude = long_val,
				timestamp = timestamp,
				heading = heading
			))

	def test_valid_emit(self):
		vID = uuid.uuid4().hex
		rv = self.emit(vID, 'taxi', 53.067723, -4.07495, '22-12-2016 00:01:12', 1)
		assert b'Success!' in rv.data

	def test_invalid_id(self):
		vID = '12notaUUID'
		rv = self.emit(vID, 'taxi', 53.067723, -4.07495, '22-12-2016 00:01:12', 1)
		assert b'Vehicle ID or vehicle type is invalid' in rv.data

	def test_invalid_type(self):
		vID = uuid.uuid4().hex
		rv = self.emit(vID, 'unicorn', 53.067723, -4.07495, '22-12-2016 00:01:12', 1)
		assert b'Vehicle ID or vehicle type is invalid' in rv.data

	def test_far_point(self):
		vID = uuid.uuid4().hex
		rv = self.emit(vID, 'taxi', 31.2319326, 29.9492453, '22-12-2016 00:01:12', 1)
		assert b'Co-ordinates/heading invalid' in rv.data

	def test_invalid_timestamp(self):
		vID = uuid.uuid4().hex
		rv = self.emit(vID, 'taxi', 53.067723, -4.07495, '00:01:12', 1)
		assert b'Invalid value(s) provided' in rv.data

	def test_invalid_heading(self):
		vID = uuid.uuid4().hex
		rv = self.emit(vID, 'taxi', 53.067723, -4.07495, '22-12-2016 00:01:12', 360)
		assert b'Co-ordinates/heading invalid' in rv.data



if __name__ == '__main__':
	unittest.main() 