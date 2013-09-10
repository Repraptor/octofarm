from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils import simplejson
import json
from models import Printer, PrinterJob
def get_status(request, ip_address):
    import urllib2
    u = urllib2.urlopen('http://%s/api/state' % (ip_address))
    return HttpResponse(u.read(), content_type="application/json")

from django.views.decorators.cache import never_cache

def get_json(request):
    response_data = {}
    response_data['name'] = 'Farm Operational Control'
    printers = Printer.objects.all()
    response_data['stats'] = {}
    on_printers_external_html_ids = []
    on_printers = []
    for i, printer in enumerate(printers):
        if printer.get_operational_status() != 'not connected to network':
            on_printers_external_html_ids.append(i)
            on_printers.append(printer)
    #printers = on_printers
    try:
        response_data['stats']['printers_printing'] = len([printer.get_operational_status() for printer in printers if printer.get_operational_status() == 'printing'])
        print 'printers printing: ', [printer.get_operational_status() for printer in printers if printer.get_operational_status() == 'printing']
        response_data['stats']['printers'] = len(printers)
        response_data['stats']['printers_printing_percentage'] = int(float(response_data['stats']['printers_printing'] / response_data['stats']['printers']) * 100)
        #response_data['printers'] = [get_printer_status_message(request, printer.id).content for printer in Printer.objects.all()]
        #response_data['on_printers'] = on_printers
        
    except:
        pass
    try:
        import urllib2
        temp= urllib2.urlopen('http://10.0.1.5/temp/', timeout=2).read().split('\n')
        response_data['humidity'] = float(temp[0])
        response_data['temperature'] = float(temp[1])
        response_data['light'] = int(temp[2])
        response_data['fan'] = int(temp[3])
    except:
        pass

    response_data['printers'] = [get_printer_status_message(request, printer.id).content for printer in Printer.objects.all()]
    response_data['on_printers_external_streaming_addresses'] = [printer.external_streamer_address for printer in on_printers]
    response_data['on_printers_external_html_ids'] = on_printers_external_html_ids
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def get_operational_status(context):
    #print 'print time left: ', context['progress_printTimeLeft']
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

@never_cache
def get_printer_status_message(request, printer_id):
    
    
    printer = Printer.objects.get(id=printer_id)
   
    context = {'printer': printer}
    status_dict = printer.get_status_dict()
    try:
        status_dict = printer.get_status_dict()
    except:
        context['operational_status'] = 'not connected to network'
        return render_to_response('printer_status_message.html', context)
    if 'connection' in status_dict:
        context['operational_status'] = 'not connected to network'
        return render_to_response('printer_status_message.html', context)
    for key, d in status_dict.items():
        context[key] = d
        if type(d) is dict:
            for key2, d2 in d.items():
                context[key + '_' + key2] = d2
                if type(d2) is dict:
                    for key3, d3 in d2.items():
                        context[key + '_' + key2 + '_' + key3] = d3

    context['percentage_done'] = int(context['progress_progress'] * 100) if context['progress_progress'] else 0
    context['operational_status'] = get_operational_status(context)
    print context.keys()
    #try:
     #   printer_job = PrinterJob(printer=printer, file_name=context['job_filename'], filament_amount_used=int(float(context['job_filament'].replace('m', ''))))
    #    printer_job.status = context['operational_status']
    #    printer_job.save()
    #except:
    #    pass
    return render_to_response('printer_status_message.html', context)

def get_printer_history(request, printer_id):
    printer = Printer.objects.get(id=printer_id)
   
    context = {'printer': printer}
    return render_to_response('printer_history.html', context) 

def change_device(request, device, action):
    the_bool = 1 if action == 'on' else 0
    import urllib2
    print 'http://10.0.1.5/%s/%s/' % (device, the_bool)
    response = urllib2.urlopen('http://10.0.1.5/%s/%s/' % (device, the_bool))
    print response.info()
    html = response.read()
    # do something
    response.close()
    return HttpResponse('')
