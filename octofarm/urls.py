from django.conf.urls import patterns, include, url
from django.views.generic import ListView
from models import Printer
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'octoprintmonitor.views.home', name='home'),
    # url(r'^octoprintmonitor/', include('octoprintmonitor.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', ListView.as_view(model=Printer, template_name='printers.html')),
    url(r'^get_status/(?P<ip_address>[\d\.]+)/$', 'octoprintmonitor.views.get_status'),
    url(r'^json/$', 'octoprintmonitor.views.get_json'),
    url(r'^turn_(?P<device>fan|lights)_(?P<action>on|off)/$', 'octoprintmonitor.views.change_device'),
    url(r'^get_printer_status_message/(?P<printer_id>\d+)/$', 'octoprintmonitor.views.get_printer_status_message'),
    url(r'^printer_history/(?P<printer_id>\d+)/$', 'octoprintmonitor.views.get_printer_history'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
)
