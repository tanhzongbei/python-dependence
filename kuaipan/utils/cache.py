# coding:utf8
"""

Author: ilcwd
"""
import functools
import logging
import hashlib

from memcache import Client as MCClient


__all__ = [
    'CacheException',
    'MemCache',
    'CacheContext',
    'FrequencyControl'
]

_logger = logging.getLogger(__name__)


class CacheException(Exception):
    pass


class MemCacheWrapper(object):
    """
    Memcache client wrapper.
    No exception raise and add some useful function.
    """

    def __init__(self, servers, logerr=None):
        self.cache = MCClient(servers=servers, debug=False)
        self.logerr = logerr

    def add(self, key, val=1, time=0):
        try:
            return self.cache.add(key, val, time)
        except Exception as e:
            _logger.warning("Exception during `add`: %s", e)

        return None

    def count(self, key, expires=0, delta=1):
        try:
            result = self.cache.incr(key, delta)
            if result is None:
                if not self.cache.add(key, delta, expires):
                    result = self.cache.incr(key, delta)
                else:
                    return delta
            return result
        except Exception as e:
            _logger.warning("Exception during `count`: %s", e)

        return None

    def get(self, key):
        result = None
        try:
            result = self.cache.get(str(key))
        except Exception as e:
            _logger.warning("Exception during `get`: %s", e)

        return result

    def set(self, key, value, expires):
        result = False
        try:
            result = self.cache.set(str(key), value, expires)
        except Exception as e:
            _logger.warning("Exception during `set`: %s", e)

        return result

    def delete(self, key):
        result = False
        try:
            result = self.cache.delete(key)
        except Exception as e:
            _logger.warning("Exception during `del`: %s", e)

        return result


def all_cache_filter(value):
    return True


def not_none_cache_filter(value):
    return value is not None


class CacheContext(object):
    def __init__(self, backend, prefix, cache_filter=not_none_cache_filter, expires=0):
        self.backend = backend
        self.prefix = prefix
        self.cache_filter = cache_filter
        self.expires = expires

    def key_dumps(self, key):
        return str(self.prefix + key)

    def cacheset(self, func):
        @functools.wraps(func)
        def _wrapper(k, v):
            res = func(k, v)
            if res:
                key = self.key_dumps(k)
                self.backend.set(key, v, self.expires)
            return res

        return _wrapper

    def cachedelete(self, func):
        @functools.wraps(func)
        def _wrapper(k):
            res = func(k)

            if res:
                key = self.key_dumps(k)
                self.backend.delete(key)
            return res

        return _wrapper

    def cacheget(self, func):
        @functools.wraps(func)
        def _wrapper(k):

            key = self.key_dumps(k)
            value = self.backend.get(key)
            if value:
                return value

            value = func(k)
            if self.cache_filter(value):
                self.backend.set(key, value, self.expires)

            return value
        return _wrapper


class FrequencyControl(object):
    """
    Use memcache to control frequency.
    It depends on memcache, it's not so accurate.

    Examples:

        frq = CacheFrequencyControl(memcacheClient, "API@", 24 * 3600)
        # ... do other thing

        if frq.incr("someAPI") > 100:
            raise Exception("Reach daily quota(100).")
    """
    def __init__(self, backend, prefix, expires=0):
        self.prefix = str(prefix)
        self.expires = int(expires)
        self.backend = backend

    def dump_key(self, key):
        return self.prefix + hashlib.sha1(key).hexdigest()

    def incr(self, key, delta=1):
        real_key = self.dump_key(key)
        result = self.backend.incr(real_key, delta)
        if result is None:
            if not self.backend.add(real_key, delta, self.expires):
                # race condition
                return self.backend.incr(real_key, delta)
            return delta
        return result


def main():
    mc = MemCacheWrapper(['10.0.3.184:11211', '10.0.3.184:11211'])


    mycache = CacheContext(mc, prefix='hehe@')

    @mycache.cacheget
    def hehe(k):
        r = 'hello:' + k
        print "Hehe RPC", r
        return r

    mycache = CacheContext(mc, prefix='haha@')
    @mycache.cacheget
    def haha(a):
        print "Haha RPC"
        return None


    hehe("1")
    hehe("2")
    hehe("3")
    haha("1")
    haha("122")


if __name__ == '__main__':
    main()
