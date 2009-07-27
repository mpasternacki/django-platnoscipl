import hashlib
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

def gen_ts():
    if uuid is not None:
        return str(uuid.uuid1())
    else:
        return str(time.time())

class CurrentPaymentManager(models.Manager):
    def get_query_set(self):
        return super(CurrentPaymentManager, self) \
               .get_query_set() \
               .filter(is_current=True)

    def fetch_xml(self, session_id):
        ts = gen_ts()
        data = {
            'pos_id': str(conf.POS_ID),
            'session_id': session_id,
            'ts': ts,
            }
        data['sig'] = hashlib.md5(
            data['pos_id']
            + data['session_id']
            + data['ts']
            + conf.KEY1).hexdigest()

        return urllib2.urlopen(
            conf.ENDPOINT+'Payment/get/xml',
            urllib.urlencode(data)).read()

    def update(self, session_id=None, instance=None, xml=None, save=True):
        assert bool(session_id) <> bool(instance) # poor man's xor

        if session_id:
            try:
                instance = self.get(session_id=session_id)
            except self.model.DoesNotExist:
                instance = None
        else:
            session_id = instance.session_id

        if xml is None:
            xml = self.fetch_xml(session_id)
        et = ET.fromstring(xml)

        assert et[0].text == 'OK'       # FIXME

        def _f(path):
            f = et[1].find(path)
            if f is not None:
                return f.text
        rv = self.model(
            transaction_id = _f('id'),
            pos_id = _f('pos_id'),
            session_id = _f('session_id'),
            order_id = _f('order_id'),
            amount = _f('amount'),
            status = _f('status'),
            pay_type = _f('pay_type'),
            pay_gw_name = _f('pay_gw_name'),
            desc = _f('desc'),
            desc2 = _f('desc2'),
            create = _f('create'),
            init = _f('init'),
            sent = _f('sent'),
            recv = _f('recv'),
            cancel = _f('cancel'),
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
    status = models.IntegerField(choices=constants.STATE_NAMES.items())
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
        return hashlib.md5(''.join((
            str(self.pos_id),
            self.session_id,
            str(self.order_id),
            str(self.status),
            str(self.amount),
            self.desc.encode('utf-8'),
            self.ts,
            conf.KEY2,
            ))).hexdigest()

    def get_amount_display(self):
        return self.amount / 100.       # FIXME:decimal

    def check_signature(self):
        assert self.sig == self.get_signature()

    def update(self, save=True):
        return self.objects.update(instance=self, save=save)[0]


def get_order_model():
    if conf.ORDER_MODEL:
        app_label, model_name = conf.ORDER_MODEL.split('.')
        return models.get_model(app_label, model_name)
