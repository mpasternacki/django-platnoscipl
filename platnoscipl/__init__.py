from django.core.exceptions import ImproperlyConfigured

try:
    from conf import *
except Exception, e:
    raise ImproperlyConfigured("Misconfigured: %s" % e)
