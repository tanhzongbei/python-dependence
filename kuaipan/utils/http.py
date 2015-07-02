# coding:utf8
"""
@Author: Ilcwd
"""

import StringIO
import pycurl
import ujson as json
import urllib
from threading import local
import logging

_logger = logging.getLogger(__name__)

DEFAULT_USER_AGENT = 'Kuaipan HTTP/PycURL' + pycurl.version_info()[1]


class HTTPError(Exception):
    pass


def show_info(c):
    print '-' * 80
    infos = ['EFFECTIVE_URL', 'RESPONSE_CODE', 'NUM_CONNECTS',
             'TOTAL_TIME', 'NAMELOOKUP_TIME', 'CONNECT_TIME', 'APPCONNECT_TIME',
             'PRETRANSFER_TIME', 'STARTTRANSFER_TIME', 'REDIRECT_TIME']
    for info in infos:
        print info, ':', c.getinfo(getattr(pycurl, info))
    print '-' * 80


class HTTPConnection(local):
    DEFAULT_TIMEOUT = 30

    def __init__(self, host, keepalive=1, raise_exception=False):
        self.host = str(host)
        self.keepalive = keepalive
        self.raise_exception = raise_exception

        # overwrite `Expect` to avoid 100-continue waiting .
        self.default_headers = {
            'Expect': '',
            'User-Agent': DEFAULT_USER_AGENT,
        }
        self.context = None
        if keepalive:
            self.context = pycurl.Curl()
            self.default_headers['Connection'] = 'Keep-Alive'
            self.default_headers['Keep-Alive'] = '300'

    def close(self):
        if self.keepalive:
            self.context.close()

    def get(self, path, query=None, headers=None, timeout=None):
        if query:
            querystring = urllib.urlencode(query)
            path = path + '?' + querystring

        return self.request(path, headers=headers, timeout=timeout)

    def post_json(self, path, query, headers=None, timeout=None):
        if not headers:
            headers = {}

        headers['Content-Type'] = 'application/json'
        post = json.dumps(query)
        return self.request(path, post, headers=headers, timeout=timeout)

    def request(self, path, postdata=None, headers=None, timeout=None):
        buf = StringIO.StringIO()

        if self.keepalive:
            context = self.context
        else:
            context = pycurl.Curl()

        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT

        url = self.host + str(path)
        context.setopt(pycurl.URL, url)
        context.setopt(pycurl.WRITEFUNCTION, buf.write)
        context.setopt(pycurl.CONNECTTIMEOUT, timeout)
        context.setopt(pycurl.TIMEOUT, timeout)
        t_header = self.default_headers.copy()

        if headers:
            t_header.update(headers)

        headerlist = []
        for k, v in t_header.iteritems():
            item = '%s: %s' % (k, v)
            if isinstance(item, unicode):
                item = item.encode('utf-8')
            headerlist.append(item)

        context.setopt(pycurl.HTTPHEADER, headerlist)

        if postdata:
            if isinstance(postdata, unicode):
                postdata = postdata.encode('utf-8')

            context.setopt(pycurl.POSTFIELDS, postdata)

        try:
            context.perform()
            code = context.getinfo(pycurl.RESPONSE_CODE)
            result = buf.getvalue()
            return code, result
        except (pycurl.error, Exception) as e:
            _logger.info("Connect to `%s` fail: %s", url, e)
            if self.raise_exception:
                raise HTTPError(e)

            return 599, None
        finally:
            buf.close()
            if not self.keepalive:
                context.close()
            else:
                # if not reset, cookies, post data, etc will be remained for next request.
                # we just want to preserve connections,
                context.reset()


def main():
    httpconn = HTTPConnection("http://10.0.3.184")
    print httpconn.post_json('/open/time', {'a': 'a'* 1024})
    print httpconn.get('/open/time')
    print httpconn.get('/open/time')
    print httpconn.get('/open/time')

    import threading

    def work():
        for i in xrange(10):
            assert httpconn.get('/open/time')[0] == 200

    threads = []
    for i in xrange(5):
        t = threading.Thread(target=work)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print "fin"


if __name__ == '__main__':
    main()
