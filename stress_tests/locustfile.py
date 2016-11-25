#!/usr/bin/env python
import uuid
from datetime import datetime
from math import radians, degrees, sqrt, pi, cos, sin
from random import random, randint
from locust import HttpLocust, TaskSet, task

snowdonia_center = (53.068889, -4.075556)
types = ['taxi', 'tram', 'bus', 'train']
numbers = dict(taxi=0, tram=0, bus=0, train=0)

def req_data(vType):
    pt = generate_point()
    heading = randint(0, 359)
    return {
        'type': vType,
        'latitude': pt['latitude'],
        'longitude': pt['longitude'],
        'heading': heading,
        'timestamp': datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    }

def url(vID):
    return '/api/v1/emission/' + vID

def vType():
    return types[randint(0,3)]

def generate_point():
    r = 50000/111300
    u, v = random(), random()
    y0, x0 = snowdonia_center
    w = r * sqrt(u)
    t = 2 * pi * v
    x = w * cos(t)
    y = w * sin(t)
    x1 = x / cos(y0)
    return dict(longitude=x1+x0, latitude=y+y0)

def emit(l, vID):
    l.client.post(url(vID), req_data())

class Emission(TaskSet): 
    def on_start(self):
        self.vID = uuid.uuid4().hex
        self.vType = vType()
        self.num = numbers[self.vType] + 1
        numbers[self.vType] += 1

    @task(1)
    def emit(self):
        data = req_data(self.vType)
        lat_long_str = data['type'] + '-' + str(self.num) +\
                ' at ' +\
                str((data['latitude'], data['longitude']))
        self.client.post(url(self.vID), data, name=lat_long_str)
        

class APIUser(HttpLocust):
    task_set = Emission
    host = 'http://snowdonia-transport.herokuapp.com'
    min_wait = 20000
    max_wait = 20000


