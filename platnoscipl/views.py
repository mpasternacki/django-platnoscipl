# -*- python; coding: utf-8 -*-

import hashlib

from django.http import HttpResponse, HttpResponseRedirect, \
     HttpResponseForbidden
from django.views.generic.simple import direct_to_template

import conf
import constants
import models


def confirmation_screen(request,
                        template='platnoscipl/confirm.html',
                        extra_context={}):
    if 'pos_id' in request.GET:         # FIXME: do something sensible
        assert int(request.GET['pos_id']) == int(conf.POS_ID)

    c = extra_context.copy()

    def _parm(name, default='brak'):    # We get empty strings in URL
        return request.GET.get(name, None) or default

    c['transaction_id'] = _parm('transaction_id')
    c['pay_type'] = constants.PAY_TYPES.get(
        _parm('pay_type', None),
        _parm('pay_type', u'Niemożliwe!'))
    c['session_id'] = _parm('session_id')
    c['amount'] = _parm('amount')
    c['amount_with_dot'] = _parm('amount_with_dot', None)
    c['order_id'] = _parm('order_id')
    c['error'] = constants.ERR_MESSAGES.get(int(_parm('error', -1)))

    _M = models.get_order_model()
    if _M:
        try:
            c['order'] = _M.objects.get(pk=c['order_id'])
        except _M.DoesNotExist:
            pass

    return direct_to_template(request, template, extra_context=c)


def notification_handler(request):
    if request.method <> 'POST':
        return HttpResponseForbidden()

    print request.POST

    # FIXME: do something sensible
    assert int(request.POST['pos_id']) == int(conf.POS_ID)
    assert request.POST['sig'] == hashlib.md5('%s%s%s%s' % (
        conf.POS_ID,
        request.POST['session_id'],
        request.POST['ts'],
        conf.KEY2)).hexdigest()

    payment = models.Payment.objects.get_or_create(
        session_id=request.POST['session_id'])
    payment.update()
    payment.save()

    return HttpResponse('OK')
