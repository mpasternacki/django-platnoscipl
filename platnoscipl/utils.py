import hashlib

def sig(*args):
    args = [unicode(arg or u'').encode('utf-8')
            for arg in args]
    args = ''.join(args)
    rv = hashlib.md5(args).hexdigest()
    return rv
