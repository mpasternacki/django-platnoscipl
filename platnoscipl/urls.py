from django.conf.urls.defaults import *

from views import confirmation_screen, notification_handler

urlpatterns = patterns('',
                       url(r'^ok/$',
                           confirmation_screen,
                           {'template': 'platnoscipl/confirmation_ok.html'},
                           name='platnoscipl_confirmation_ok'),
                       url(r'^fail/$',
                           confirmation_screen,
                           {'template': 'platnoscipl/confirmation_fail.html'},
                           name='platnoscipl_confirmation_fail'),
                       url(r'^notify/$', notification_handler,
                           name='platnoscipl_notification_handler'),
                       )
