import time

try:
    from config import config
except ImportError:
    config = {'debug':True}

def time_instrument(method):
    
    if config["debug"] == False:
        return method

    def timed_func(*args, **kw):

        time_started = time.time()

        result = method(*args, **kw)

        time_ended = time.time()

        print '%r (%r, %r) %2.2f sec' % \
              (method.__name__, args, kw, time_ended - time_started)
        return result

    return timed_func