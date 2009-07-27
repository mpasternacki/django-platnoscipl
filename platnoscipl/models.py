import urllib
import urllib2
import xml.etree.ElementTree as ET # FIXME: proper import cascade for older pythons

try:
    import uuid
except ImportError:
    import time
    uuid = None

from django.db import models

import conf
import constants
from utils import sig

def gen_ts():
    if uuid is not None:
        return str(uuid.uuid1())
    else:
        return str(time.time())

# Silly hack to re-use Django's date parsing magic
parse_datetime = models.DateTimeField().to_python

class CurrentPaymentManager(models.Manager):
    def get_query_set(self):
        return super(CurrentPaymentManager, self) \
               .get_query_set() \
               .filter(is_current=True)

    def rpc(self, session_id, method):
        ts = gen_ts()
        data = {
            'pos_id': str(conf.POS_ID),
            'session_id': session_id,
            'ts': ts,
            }
        data['sig'] = sig(
            data['pos_id'],
            data['session_id'],
            data['ts'],
            conf.KEY1,
            )

        return urllib2.urlopen(
            '%sPayment/%s/xml' % (conf.ENDPOINT, method),
            urllib.urlencode(data)).read()

    def reload(self, session_id=None, instance=None, xml=None, save=True):
        assert bool(session_id) <> bool(instance) # poor man's xor

        if session_id:
            try:
                instance = self.get(session_id=session_id)
            except self.model.DoesNotExist:
                instance = None
        else:
            session_id = instance.session_id

        if xml is None:
            xml = self.rpc(session_id, 'get')
        et = ET.fromstring(xml)

        assert et[0].text == 'OK'       # FIXME

        def _f(path):
            f = et[1].find(path)
            if f is not None:
                return f.text or None
        rv = self.model(
            transaction_id = _f('id'),
            pos_id = int(_f('pos_id')),
            session_id = _f('session_id'),
            order_id = _f('order_id'),
            amount = int(_f('amount')),
            status = int(_f('status')),
            pay_type = _f('pay_type'),
            pay_gw_name = _f('pay_gw_name'),
            desc = _f('desc'),
            desc2 = _f('desc2'),
            create = parse_datetime(_f('create')),
            init = parse_datetime(_f('init')),
            sent = parse_datetime(_f('sent')),
            recv = parse_datetime(_f('recv')),
            cancel = parse_datetime(_f('cancel')),
            auth_fraud = _f('auth_fraud'),
            ts = _f('ts'),
            sig = _f('sig'),
            add_cc_number_hash = _f('add_cc_number_hash'),
            add_cc_bin = _f('add_cc_bin'),
            add_cc_number = _f('add_cc_number'),
            add_owner_name = _f('add_owner_name'),
            add_owner_address = _f('add_owner_address'),
            add_trans_title = _f('add_trans_title'),
            add_bank_name = _f('add_bank_name'),
            add_trans_prev = _f('add_trans_prev'),
            add_trans_add_desc = _f('add_trans_add_desc'),
            add_test = _f('add_test'),
            add_testid = _f('add_testid'),
            )

        rv.check_signature()

        if save:
            if instance:
                instance.is_current = False
                instance.save()
            rv.is_current = True
            rv.save()

        return rv, instance

class Payment(models.Model):
    all_objects = models.Manager()
    objects = CurrentPaymentManager()

    # bookkeeping
    is_current = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now=True)

    # platnosci.pl info
    transaction_id = models.CharField(max_length=255)
    pos_id = models.IntegerField()
    session_id = models.CharField(max_length=1024)
    if conf.ORDER_MODEL:
        order = models.ForeignKey(conf.ORDER_MODEL)
    else:
        order_id = models.CharField(max_length=255)
    amount = models.IntegerField()
    status = models.IntegerField(choices=constants.STATUS_NAMES.items())
    pay_type = models.CharField(max_length=2,
                                choices=constants.PAY_TYPES.items())
    pay_gw_name = models.CharField(max_length=64)
    desc = models.CharField(max_length=1024)
    desc2 = models.CharField(max_length=1024, null=True, blank=True)
    create = models.DateTimeField()
    init = models.DateTimeField(null=True, blank=True)
    sent = models.DateTimeField(null=True, blank=True)
    recv = models.DateTimeField(null=True, blank=True)
    cancel = models.DateTimeField(null=True, blank=True)
    auth_fraud = models.CharField(max_length=255)
    ts = models.CharField(max_length=255)
    sig = models.CharField(max_length=32)
    add_cc_number_hash = models.CharField(max_length=255, null=True, blank=True)
    add_cc_bin = models.CharField(max_length=255, null=True, blank=True)
    add_cc_number = models.CharField(max_length=255, null=True, blank=True)
    add_owner_name = models.CharField(max_length=255, null=True, blank=True)
    add_owner_address = models.CharField(max_length=255, null=True, blank=True)
    add_trans_title = models.CharField(max_length=255, null=True, blank=True)
    add_bank_name = models.CharField(max_length=255, null=True, blank=True)
    add_trans_prev = models.CharField(max_length=255, null=True, blank=True)
    add_trans_add_desc = models.CharField(max_length=255, null=True, blank=True)
    add_test = models.CharField(max_length=1, null=True, blank=True)
    add_testid = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.session_id

    def __nonzero__(self):
        return bool(self.id)

    def get_signature(self):
        return sig(
            self.pos_id,
            self.session_id,
            self.order_id,
            self.status,
            self.amount,
            self.desc,
            self.ts,
            conf.KEY2,
            )

    def get_amount_display(self):
        return self.amount / 100.       # FIXME:decimal

    def check_signature(self):
        assert self.sig == self.get_signature()

    def reload(self, save=True):
        return self.__class__.objects.reload(instance=self, save=save)[0]

    def rpc(self, method):
        return self.__class__.objects.rpc(self.session_id, method)

    def _confirm_or_cancel(self, method, reload):
        assert self.status == constants.STATUS_PENDING

        et = ET.fromstring(self.rpc('confirm'))
        assert et[0].text == 'OK'       # FIXME: handle errors

        assert int(et[1].find('pos_id').text) == int(self.pos_id)
        assert et[1].find('session_id').text == self.session_id
        assert sig(
            self.pos_id,
            self.session_id,
            et[1].find('ts').text,
            conf.KEY2,
            ) == et[1].find('sig').text

        if reload:
            return self.reload()

    def do_confirm(self, reload=True):
        return self._confirm_or_cancel('confirm', reload)

    def do_cancel(self, reload=True):
        return self._confirm_or_cancel('cancel', reload)

def get_order_model():
    if conf.ORDER_MODEL:
        app_label, model_name = conf.ORDER_MODEL.split('.')
        return models.get_model(app_label, model_name)
