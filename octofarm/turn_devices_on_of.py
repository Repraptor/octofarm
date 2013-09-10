from django.core.management import setup_environ
import settings

setup_environ(settings)

import time
from models import DeviceOnOff

while True: 
    for i in DeviceOnOff.objects.all():
        import urllib2
        temp = urllib2.urlopen('http://10.0.1.5/temp/', timeout=2).read()
        # get sensor data
        indexes = {'temp': 1, 'humidity': 0}
        sensor_data = temp.split('\n')[indexes[i.sensor.name]]
        print '%s %s' % (i.device.name, i.sensor.name)
        if i.on:
           if float(sensor_data) > i.threshold:
               urllib2.urlopen('http://10.0.1.5/%s/1/' % (i.device.name), timeout=2).read()
        else:
           if float(sensor_data) < i.threshold:
               urllib2.urlopen('http://10.0.1.5/%s/0/' % (i.device.name), timeout=2).read()
    time.sleep(60)

