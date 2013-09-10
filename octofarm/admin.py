from django.contrib import admin
from models import Printer, PrinterStatus, PrinterJob, TempHumidity, Device, Sensor, DeviceOnOff

admin.site.register(Printer)
admin.site.register(PrinterStatus)
admin.site.register(PrinterJob)
admin.site.register(TempHumidity)
admin.site.register(Device)
admin.site.register(Sensor)
admin.site.register(DeviceOnOff)
