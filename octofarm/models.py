from django.db import models

class Printer(models.Model):
    name = models.CharField(max_length=100)
    internal_octoprint_address = models.CharField(max_length=200)
    external_octoprint_address = models.CharField(max_length=200)
    internal_streamer_address = models.CharField(max_length=200)
    external_streamer_address = models.CharField(max_length=200)
    order = models.PositiveIntegerField()
    
    class Meta:
        app_label = 'octofarm'
        ordering = ['order']

    def __unicode__(self):
        return self.name

    def get_url(self):
        return 'http://%s/' % (self.external_octoprint_address)

    def get_history_url(self):
        #print 'get history'
        #print 'self id: ', self.id
        return '/printer_history/%s/' % (self.id)

    def get_status_dict(self):
        #print 'get status dict'
        #import urllib2
        #u = urllib2.urlopen('http://%s/api/state' % (self.internal_octoprint_address), timeout=2)
        try:
            printer_status = PrinterStatus.objects.get(printer=self)
        except:
            printer_status = PrinterStatus(printer=self)
            self.save_status()
        u = printer_status.status
        import json
        #print 'JSON ', u
        #print json.loads(u)
        return json.loads(u)

    def save_status(self):
        import urllib2
        try:
            u = urllib2.urlopen('http://%s/api/state' % (self.internal_octoprint_address), timeout=2).read()
        except:
            u = '{"connection": false}'
        try:
            printer_status = PrinterStatus.objects.get(printer=self)
        except:
            printer_status = PrinterStatus(printer=self)
        printer_status.status = u
        printer_status.save()
        #print 'Saved status for ', self.name
        return 

    def get_status(self):
        #print 'get status'
        #print self.get_status_dict().keys()
        return [(i[0], i[1].items()) if type(i[1]) is dict else i for i in self.get_status_dict().items()]
 
    def get_progress(self):
        return self.get_status_dict()['progress']

    def get_progress_progress(self):
        return self.get_status_dict()['progress']['progress']

    def get_percentage_done(self):
        return int(self.get_progress_progress() * 100)

    def get_progress_filepos(self):
        return self.get_status_dict()['progress']['filepos']

    def get_progress_printTimeLeft(self):
        return self.get_status_dict()['progress']['printTimeLeft']

    def get_progress_printTime(self):
        return self.get_status_dict()['progress']['printTime']

    def get_job(self):
        return self.get_status_dict()['job']

    def get_job_estimatedPrintTime(self):
        return self.get_status_dict()['job']['estimatedPrintTime']

    def get_job_filesize(self):
        return self.get_status_dict()['job']['filesize']

    def get_job_filament(self):
        return self.get_status_dict()['job']['filament']

    def get_job_filename(self):
        return self.get_status_dict()['job']['filename']

    def get_currentZ(self):
        return self.get_status_dict()['currentZ']

    def get_state(self):
        return self.get_status_dict()['state']

    def get_state_state(self):
        return self.get_status_dict()['state']['state']

    def get_state_stateString(self):
        return self.get_status_dict()['state']['stateString']

    def get_state_flags(self):
        return self.get_status_dict()['state']['flags']

    def get_state_flags_operational(self):
        return self.get_status_dict()['state']['flags']['operational']

    def get_state_flags_paused(self):
        return self.get_status_dict()['state']['flags']['paused']

    def get_state_flags_printing(self):
        return self.get_status_dict()['state']['flags']['printing']

    def get_operational_status(self):
        context = {}
        try:
            status_dict = self.get_status_dict()
        except:
            context['operational_status'] = 'not connected to network'
            return render_to_response('printer_status_message.html', context)
        if 'connection' in status_dict:
            return 'not connected to network'
        for key, d in status_dict.items():
            context[key] = d
            if type(d) is dict:
                for key2, d2 in d.items():
                    context[key + '_' + key2] = d2
                    if type(d2) is dict:
                        for key3, d3 in d2.items():
                            context[key + '_' + key2 + '_' + key3] = d3
        #print 'print time left: ', context['progress_printTimeLeft']
        #print '=' * 50
        #print context.keys()
        #print '=' * 50
        if context["state_stateString"] == "Sending file to SD":
            print 'State string: ', context["state_stateString"]
            return 'Saving file to SD card'
        if context['state_flags_printing']:

            if not context['progress_printTimeLeft'] or not context['currentZ']:
                return 'warming up to print'
            #if int(context['temperatures_extruder_current()'] < int(context['temperatures_extruder_target()']:
            #    return 'warming up to print'
            return 'printing'
        if context['state_flags_paused']:
            print context['progress_printTimeLeft']
            if not context['progress_printTimeLeft']:
            
                return 'warming up to print'
            return 'paused'
        if context['state_flags_operational']:
            if context['job_filename']:
                if context['temperatures_bed_current'] > 28:
                    return 'cooling after printing'

                return 'finished printing'
            return 'idle'
        return 'off'

        #print 'print time left: ', self.get_progress_printTimeLeft()
        if self.get_state_flags_printing():
            if not self.get_progress_printTimeLeft():
                return 'warming up to print'
            #if int(self.get_temperatures_extruder_current()) < int(self.get_temperatures_extruder_target()):
            #    return 'warming up to print'
            return 'printing'
        if self.get_state_flags_paused():
            #print self.get_progress_printTimeLeft()
            if not self.get_progress_printTimeLeft():
                
                return 'warming up to print'
            return 'paused'
        if self.get_state_flags_operational():
            if self.get_job_filename():
                if self.get_temperatures_bed_current() > 28:
                    return 'cooling after printing'

                return 'finished printing'
            return 'idle'
        return 'off'

    def get_state_flags_sdReady(self):
        return self.get_status_dict()['state']['flags']['sdReady']

    def get_state_flags_error(self):
        return self.get_status_dict()['state']['flags']['error']

    def get_state_flags_ready(self):
        return self.get_status_dict()['state']['flags']['ready']

    def get_state_flags_closedOrError(self):
        return self.get_status_dict()['state']['flags']['closedOrError']

    def get_temperatures(self):
        return self.get_status_dict()['temperatures']

    def get_temperatures_bed(self):
        return self.get_status_dict()['temperatures']['bed']

    def get_temperatures_bed_current(self):
        return self.get_status_dict()['temperatures']['bed']['current']

    def get_temperatures_bed_target(self):
        return self.get_status_dict()['temperatures']['bed']['target']

    def get_temperatures_extruder(self):
        return self.get_status_dict()['temperatures']['extruder']

    def get_temperatures_extruder_current(self):
        return self.get_status_dict()['temperatures']['extruder']['current']

    def get_temperatures_extruder_target(self):
        return self.get_status_dict()['temperatures']['extruder']['target']

    def get_history(self):
        return PrinterJob.objects.filter(printer=self).order_by('-started_warming')

    def get_history_by_dates(self):
        
        dates = sorted(list(set(PrinterJob.objects.filter(printer=self).values_list('date', flat=True))))[::-1]
        return [(date, PrinterJob.objects.filter(printer=self, date=date)) for date in dates]

    def save_job(self):
        print self.get_operational_status()
        #print 'save job'
        from django.db.models.loading import get_model
        PrinterJob = get_model('octofarm', 'PrinterJob')
        if not 'job' in self.get_status_dict():
            #print 'no job filename', self.get_status_dict().keys()
            return
        printer_jobs = PrinterJob.objects.filter(printer=self, file_name=self.get_status_dict()['job']['filename']).order_by('-started_warming')
        create_new = True
        if not printer_jobs and self.get_operational_status() != 'warming up to print':
            return
        if printer_jobs:
            printer_job = printer_jobs[0]
            if printer_job.status == self.get_operational_status() or printer_job.status != 'finished printing':
                create_new = False
            if self.get_operational_status() == 'warming up to print' and printer_job.status != 'warming up to print':
                printer_job.status = 'finished printing'
                import datetime
                current_time = datetime.datetime.now()
                printer_job.finished_printing = current_time
                printer_job.save()
                create_new = True
        if not self.get_status_dict()['job']['filename']:
            return
        if self.get_operational_status() == 'finished printing' and printer_job.status != 'finished printing':
            from django.core.mail import send_mail
            send_mail('Done printing on %s' % (self.name), 'Done printing on %s' % (self.name), 'timothy.clemans@gmail.com', ['timothy.clemans@gmail.com'], fail_silently=False)

        if create_new:
            #print 'else'
            filament = 0
            if self.get_status_dict()['job']['filament'] is not None:
                filament = int(float(self.get_status_dict()['job']['filament'].replace('m', ''))) if self.get_status_dict()['job']['filament'] else 0
            printer_job = PrinterJob(printer=self, file_name=self.get_status_dict()['job']['filename'], filament_amount_used=filament)
        #print self.get_status_dict()
        if printer_job.status and self.get_operational_status() != printer_job.status:
            status = self.get_operational_status()
            import datetime
            current_time = datetime.datetime.now()
            
            if status == 'printing':
                printer_job.started_printing = current_time
            if status == 'finished printing':
                printer_job.finished_printing = current_time
            if status == 'finished cooling':
                printer_job.finished_cooling = current_time
            printer_job.status = self.get_operational_status()
        import urllib, os
        from urlparse import urlparse
        print 'http://%s/?action=snapshot' % (self.internal_streamer_address)
        if self.get_operational_status() != 'finished printing':
            print self.get_operational_status()
            print self.internal_streamer_address
            import socket
            socket.setdefaulttimeout(5)
            try:
                urllib.urlretrieve('http://%s/?action=snapshot' % (self.internal_streamer_address), "static/images/printer_jobs/printer_job_%s.jpg" % (printer_job.id))
            except:
                pass
        #print float(self.get_status_dict()['job']['filament'].replace('m', ''))
        #print round(float(self.get_status_dict()['job']['filament'].replace('m', '')))
        printer_job.filament_amount_used = int(round(float(self.get_status_dict()['job']['filament'].replace('m', '')))) if self.get_status_dict()['job']['filament'] else 0
        printer_job.save()
       

    def get_print_times_for_filename(self, filename):
        jobs = PrinterJob.objects.filter(printer=self, file_name=filename, started_warming__isnull=False, started_printing__isnull=False, finished_printing__isnull=False, status='finished printing')
        return [job.total_time() for job in jobs]

    def get_print_times_for_current_filename(self):
        return self.get_print_times_for_filename(self.get_job_filename())

    def get_warmup_times_for_filename(self, filename):
        jobs = PrinterJob.objects.filter(printer=self, file_name=filename, started_warming__isnull=False, started_printing__isnull=False, finished_printing__isnull=False, status='finished printing')
        print 'warm up times: ', [job.time_to_warm_up() for job in jobs]
        return [job.time_to_warm_up() for job in jobs]

    def get_warmup_times_for_current_filename(self):
        return self.get_warmup_times_for_filename(self.get_job_filename())

    def is_prediction_ready():
        return bool(len(get_warmup_times_for_current_filename(self)) > 0)

    def get_min_time(self):
        
        return min(self.get_print_times_for_current_filename())

    def get_max_time(self):
        return max(self.get_print_times_for_current_filename())

    def get_min_warmup(self):
        print 'min warmup ', min(self.get_warmup_times_for_current_filename())
        return min(self.get_warmup_times_for_current_filename())

    def get_max_warmup(self):
        print 'max warmup ', max(self.get_warmup_times_for_current_filename())
        return max(self.get_warmup_times_for_current_filename())

    def get_job(self):
        print 'get_job'
        print self.get_job_filename()
        print 'query set for get job %s:' % self.name, PrinterJob.objects.filter(printer=self, file_name=self.get_job_filename())
        print 'job for %s:' % (self.name), PrinterJob.objects.filter(printer=self, file_name=self.get_job_filename())[0]
        return PrinterJob.objects.filter(printer=self, file_name=self.get_job_filename())[0]

    def time_so_far(self):
        print 'Get time so far for %s' % (self.name)
        print_job = self.get_job()
        print 'the print job ', print_job
        print 'the print job started warming for  %s' % (self.name), print_job.started_warming
        from django.utils import timezone
        current_time = timezone.now()
        print 'current time for job for %s:' % (self.name), current_time 
        d = current_time - print_job.started_warming
        print 'difference in time for job for %s:' % (self.name), d
        print 'time so far for job for %s:' % (self.name), '%s:%s' % (d.seconds//3600, prepend_zero((d.seconds//60)%60))  
        return '%s:%s' % (d.seconds//3600, prepend_zero((d.seconds//60)%60))  

    def time_left_min(self):
        print convert_to_seconds(self.get_min_time())
        print convert_to_seconds(self.time_so_far()) 
        d = convert_to_seconds(self.get_min_time()) - convert_to_seconds(self.time_so_far()) 
        return '%s:%s' % (d//3600, prepend_zero((d//60)%60)) 

    def time_left_max(self):
        print convert_to_seconds(self.get_max_time())
        print convert_to_seconds(self.time_so_far()) 
        d = convert_to_seconds(self.get_max_time()) - convert_to_seconds(self.time_so_far()) 
        return '%s:%s' % (d//3600, prepend_zero((d//60)%60))

    def til_print_min(self):
        print 'get min warmup', convert_to_seconds(self.get_min_warmup())
        print 'time so far', convert_to_seconds(self.time_so_far()) 
        d = convert_to_seconds(self.get_min_warmup()) - convert_to_seconds(self.time_so_far()) 
        print 'til print min d ', d
        return '%s' % ((d//60)%60)

    def til_print_max(self):
        print 'get max warmup', convert_to_seconds(self.get_max_warmup())
        print convert_to_seconds(self.time_so_far()) 
        d = convert_to_seconds(self.get_max_warmup()) - convert_to_seconds(self.time_so_far()) 
        return '%s' % ((d//60)%60)

class Device(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'octofarm'

    def __unicode__(self):
        return self.name

class Sensor(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'octofarm'

    def __unicode__(self):
        return self.name

class DeviceOnOff(models.Model):
    device = models.ForeignKey(Device)
    sensor = models.ForeignKey(Sensor)
    on = models.BooleanField()
    threshold = models.FloatField()

    class Meta:
        app_label = 'octofarm'

    def __unicode__(self):
        return "%s %s %s %s" % (self.device.name, self.sensor.name, self.on, self.threshold)

class TempHumidity(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    datetime = models.DateTimeField(auto_now_add=True)
    temp = models.FloatField()
    humidity = models.FloatField()

    class Meta:
        app_label = 'octofarm'
        ordering = ['-datetime']

class PrinterStatus(models.Model):
    printer = models.OneToOneField(Printer)
    status = models.TextField()

    class Meta:
        app_label = 'octofarm'
        

    def __unicode__(self):
        return self.printer.name

def prepend_zero(minute):
    if minute < 10:
        return '0' + str(minute)
    return minute

def convert_to_seconds(hm):
    hm = str(hm)
    if ':' in hm:
        h, m = hm.split(':')
        h, m = int(h), int(m)
        return h * 60 * 60 + m * 60    
    return int(hm) * 60

class PrinterJob(models.Model):
    printer = models.ForeignKey(Printer)
    file_name = models.CharField(max_length=200)
    date = models.DateField(auto_now_add=True)
    started_warming = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    started_printing = models.DateTimeField(blank=True, null=True)
    finished_first_layer = models.DateTimeField(blank=True, null=True)
    started_main_printing = models.DateTimeField(blank=True, null=True)
    finished_printing = models.DateTimeField(blank=True, null=True)
    finished_cooling = models.DateTimeField(blank=True, null=True)
    removed_from_bed = models.DateTimeField(blank=True, null=True)
    canceled_at = models.DateTimeField(blank=True, null=True)
    filament_color = models.CharField(max_length=20, default='white')
    filament_amount_used = models.PositiveIntegerField()
    filament_type = models.CharField(max_length=5, default="PLA")
    image = models.ImageField(upload_to='jobs', null=True, blank=True)
    status = models.CharField(max_length=200, default='warming up to print')
    notes = models.TextField(blank=True)

    class Meta:
        app_label = 'octofarm'
        ordering = ['-started_warming']

    def __unicode__(self):
        return self.printer.name

    def time_to_warm_up(self):
        d = self.started_printing - self.started_warming
        return d.seconds / 60

    def time_to_print(self):
        d =  self.finished_printing - self.started_printing
        return '%s:%s' % (d.seconds//3600, prepend_zero((d.seconds//60)%60))  

    def total_time(self):
        d =  self.finished_printing - self.started_warming
        return '%s:%s' % (d.seconds//3600, prepend_zero((d.seconds//60)%60))  


class FilamentReload(models.Model):
    printer = models.ForeignKey(Printer)
    datetime = models.DateTimeField(auto_now_add=True)
    filament = models.PositiveIntegerField()

    class Meta:
        app_label = 'octofarm'
