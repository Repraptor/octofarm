from django.core.management import setup_environ
import settings

setup_environ(settings)

import time
from models import TempHumidity

while True: 
    import urllib2
    temp = urllib2.urlopen('http://10.0.1.5/temp/', timeout=2).read().split('\n')
    humidity = float(temp[0])
    temp = float(temp[1])
    print temp, humidity
    th = TempHumidity(temp=temp, humidity=humidity)
    th.save()
    time.sleep(60)
