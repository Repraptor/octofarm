from django.core.management import setup_environ
import settings

setup_environ(settings)

import time
from models import Printer, PrinterJob

while True: 
    [(printer.save_status(), printer.save_job()) for printer in Printer.objects.all()]
    time.sleep(1)
