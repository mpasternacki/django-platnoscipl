# -*- python; coding: utf-8 -*-
from django.conf import settings
ENDPOINT = getattr(settings, 'PLATNOSCIPL_ENDPOINT',
                   'https://www.platnosci.pl/paygw/')
if not ENDPOINT.endswith('/'):
    ENDPOINT += '/'
ENDPOINT += 'UTF/'

POS_ID = settings.PLATNOSCIPL_POS_ID
POS_AUTH_KEY = settings.PLATNOSCIPL_POS_AUTH_KEY
KEY1 = settings.PLATNOSCIPL_KEY1
KEY2 = settings.PLATNOSCIPL_KEY2

ORDER_MODEL = getattr(settings, 'PLATNOSCIPL_ORDER_MODEL', None)
