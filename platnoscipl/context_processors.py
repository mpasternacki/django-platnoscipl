from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

import constants


def urls(request):
    return {
        'platnoscipl_urls': {
            'ok': 'http://%s%s?%s' % (
                Site.objects.get_current().domain,
                reverse('platnoscipl_confirmation_ok'),
                constants.OK_URL_QUERY_STRING),
            'fail': 'http://%s%s?%s' % (
                Site.objects.get_current().domain,
                reverse('platnoscipl_confirmation_fail'),
                constants.FAIL_URL_QUERY_STRING),
            'notify': 'http://%s%s' % (
                Site.objects.get_current().domain,
                reverse('platnoscipl_notification_handler')),
            }}
