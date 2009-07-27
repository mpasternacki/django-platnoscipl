# -*- python; coding: utf-8 -*-
try:
    from decimal import Decimal
except ImportError:

    class Decimal(object):
        """fake sentinel class to fail isinstance()"""
        pass

try:
    import uuid
except ImportError:
    import time
    uuid = None

from django import forms
from django.utils.safestring import mark_safe

import conf
import constants
from models import gen_ts
from utils import sig


class ValueHiddenInput(forms.HiddenInput): # from django-paypal
    """
    Widget that renders only if it has a value.
    Used to remove unused fields from PayPal buttons.
    """

    def render(self, name, value, attrs=None):
        if value is None:
            return u''
        else:
            return super(ValueHiddenInput, self).render(name, value, attrs)


class PlatnosciPlForm(forms.Form):
    PAY_TYPE_CHOICES = constants.PAY_TYPES.items()
    LANGUAGE_CHOICES = (('pl', 'polski'), ('en', 'english'))
    JS_CHOICES = (('0', 'nie'), ('1', 'tak'))

    pos_id = forms.IntegerField(widget=ValueHiddenInput(),
                                initial=conf.POS_ID)
    pos_auth_key = forms.CharField(widget=ValueHiddenInput(),
                                   initial=conf.POS_AUTH_KEY)
    pay_type = forms.ChoiceField(widget=ValueHiddenInput(), required=False,
                                 choices=PAY_TYPE_CHOICES)
    session_id = forms.CharField(widget=ValueHiddenInput())
    amount = forms.IntegerField(widget=ValueHiddenInput())
    desc = forms.CharField(widget=ValueHiddenInput())
    order_id = forms.CharField(widget=ValueHiddenInput(), required=False)
    desc2 = forms.CharField(widget=ValueHiddenInput(), required=False)
    trsDesc = forms.CharField(widget=ValueHiddenInput(), required=False)
    trsDesc = forms.CharField(widget=ValueHiddenInput(), required=False)
    first_name = forms.CharField(widget=ValueHiddenInput())
    last_name = forms.CharField(widget=ValueHiddenInput())
    street = forms.CharField(widget=ValueHiddenInput(), required=False)
    street_hn = forms.CharField(widget=ValueHiddenInput(), required=False)
    street_an = forms.CharField(widget=ValueHiddenInput(), required=False)
    city = forms.CharField(widget=ValueHiddenInput(), required=False)
    post_code = forms.CharField(widget=ValueHiddenInput(), required=False)
    country = forms.CharField(widget=ValueHiddenInput(), required=False)
    email = forms.CharField(widget=ValueHiddenInput())
    phone = forms.CharField(widget=ValueHiddenInput(), required=False)
    language = forms.ChoiceField(widget=ValueHiddenInput(), required=False,
                                 choices=LANGUAGE_CHOICES)
    client_ip = forms.CharField(widget=ValueHiddenInput())
    js = forms.ChoiceField(widget=ValueHiddenInput(), required=False,
                           choices=JS_CHOICES)
    payback_login = forms.CharField(widget=ValueHiddenInput(), required=False)
    sig = forms.CharField(widget=ValueHiddenInput(), required=False)
    ts = forms.CharField(widget=ValueHiddenInput(), required=False)

    def __init__(self, kwargs={}, request=None, **initial):

        # calculate integer gr from decimal pln
        if 'amount' in initial and isinstance(initial['amount'], Decimal):
            initial['amount'] = int(initial['amount']*100)

        if 'initial' in kwargs:
            kwargs['initial'].update(initial)
        else:
            kwargs['initial'] = initial

        super(PlatnosciPlForm, self).__init__(**kwargs)

        # figure out client ip if request is supplied
        if request is not None \
               and 'client_ip' not in self.initial \
               and 'REMOTE_ADDR' in request.META:
            self.initial['client_ip'] = request.META['REMOTE_ADDR']

        # use random session id if not supplied
        if uuid is not None and 'session_id' not in self.initial:
            self.initial['session_id'] = int(uuid.uuid4())

        # format session id as 16 dash-delimited digits if received as
        # number or generated
        if isinstance(self.initial['session_id'], (int, long)):
            _sid = str(self.initial['session_id'])
            self.initial['session_id'] = '%s-%s-%s-%s' % (
                _sid[0:4], _sid[4:8], _sid[8:12], _sid[12:16], )

        def _parm(name):
            return self.initial.get(name, '')

        self.initial['ts'] = gen_ts()

        self.initial['sig'] = sig(
            conf.POS_ID,
            _parm('pay_type'),
            _parm('session_id'),
            conf.POS_AUTH_KEY,
            _parm('amount'),
            _parm('desc'),
            _parm('desc2'),
            _parm('trsDesc'),
            _parm('order_id'),
            _parm('first_name'),
            _parm('last_name'),
            _parm('payback_login'),
            _parm('street'),
            _parm('street_hn'),
            _parm('street_an'),
            _parm('city'),
            _parm('post_code'),
            _parm('country'),
            _parm('email'),
            _parm('phone'),
            _parm('language'),
            _parm('client_ip'),
            _parm('ts'),
            conf.KEY1,
            )

        missing = []
        for name, field in self.fields.items():
            if field.required and not field.initial \
                   and name not in self.initial:
                missing.append(name)
        if missing:
            raise ValueError(
                "Following fields are required: %s." % ', '.join(missing))

    def get_session_id(self):
        return self.initial['session_id']

    def render(self):
        return mark_safe(u"""<form action="%sNewPayment" method="POST">
    %s
    <input type="submit" value="Zapłać poprzez Platnosci.pl" />
    </form>""" % (conf.ENDPOINT, self.as_p(), ))
