#coding:utf8
"""
Created on 2012-9-18

@author: ilcwd
"""
import time
import functools
import inspect


DEFAULT_FORMAT = '%(func)s: %(costtime)dms'


def spy_costtime(logmethod=None, name=None, formater=DEFAULT_FORMAT):
    """记录函数执行时间开销的装饰器，
    
    Args: 
        logmethod 传入参数是 name, costtime的记录日志方法
        name 如果传入，则使用这个作为函数名，否则使用 func.__name__

    Examples:

        @spy_costtime(_logger.info)
        def my_rpc():
            pass

    """

    def d(func):
        if name:
            funcname = name
        else:
            frm = inspect.stack()[1]
            mod = inspect.getmodule(frm[0])
            funcname = mod.__name__ + '.' + func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if logmethod is None:
                return func(*args, **kwargs)
        
            st = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                et = time.time()                

                costtime = int((et-st)*1000)
                params = {'func': funcname, 'costtime': costtime}
                logmethod(formater % params)

        return wrapper
    return d


def test():
    import sys

    @spy_costtime(sys.stdout.write)
    def hello():
        pass

    hello()

if __name__ == '__main__':
    test()