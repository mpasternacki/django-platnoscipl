import md5
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
    

class Payment(models.Model):
    transaction_id = models.CharField(max_length=255, unique=True)
    pos_id = models.IntegerField()
    session_id = models.CharField(max_length=1024, unique=True)
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

    def fetch_xml(self):
        ts = gen_ts()
        data = {
            'pos_id': str(self.pos_id or conf.POS_ID),
            'session_id': self.session_id,
            'ts': ts,
            }
        data['sig'] = md5.md5(
            data['pos_id']
            + data['session_id']
            + data['ts']
            + conf.KEY1).hexdigest()

        return urllib2.urlopen(
            conf.ENDPOINT+'Payment/get/xml',
            urllib.urlencode(data)).read()

    def update(self, xml=None):
        if xml is None:
            xml = self.fetch_xml()
        et = ET.fromstring(xml)

        assert et[0].text == 'OK'       # FIXME

        def _f(path):
            f = et[1].find(path)
            if f is not None:
                return f.text
        self.transaction_id = _f('id')
        self.pos_id = _f('pos_id')
        self.session_id = _f('session_id')
        self.order_id = _f('order_id')
        self.amount = _f('amount')
        self.status = _f('status')
        self.pay_type = _f('pay_type')
        self.pay_gw_name = _f('pay_gw_name')
        self.desc = _f('desc')
        self.desc2 = _f('desc2')
        self.create = _f('create')
        self.init = _f('init')
        self.sent = _f('sent')
        self.recv = _f('recv')
        self.cancel = _f('cancel')
        self.auth_fraud = _f('auth_fraud')
        self.ts = _f('ts')
        self.sig = _f('sig')
        self.add_cc_number_hash = _f('add_cc_number_hash')
        self.add_cc_bin = _f('add_cc_bin')
        self.add_cc_number = _f('add_cc_number')
        self.add_owner_name = _f('add_owner_name')
        self.add_owner_address = _f('add_owner_address')
        self.add_trans_title = _f('add_trans_title')
        self.add_bank_name = _f('add_bank_name')
        self.add_trans_prev = _f('add_trans_prev')
        self.add_trans_add_desc = _f('add_trans_add_desc')
        self.add_test = _f('add_test')
        self.add_testid = _f('add_testid')

        self.check_signature()
            

def get_order_model():
    if conf.ORDER_MODEL:
        app_label, model_name = conf.ORDER_MODEL.split('.')
        return models.get_model(app_label, model_name)
