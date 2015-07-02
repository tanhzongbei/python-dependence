# coding:utf8
"""

Author: ilcwd
"""
import json
from collections import namedtuple
import re

_MAPPING = {
    'str': str,
    'int': int,
}

_NOT_SET_ = object()


class BaseConfig(object):
    """
    Global application *read-only* configuration.

    Examples:

        See test() below.

    """

    @classmethod
    def load_config(cls, config):
        config = config.copy()
        for k, v in cls.__dict__.iteritems():
            if k.startswith('_') or k == 'load_config':
                continue

            value = config.get(k, _NOT_SET_)
            if isinstance(v, type):
                if hasattr(v, 'load_config'):
                    v.load_config(config[k])
                    value = v
                else:
                    value = v(**config[k])
            elif isinstance(v, (str, unicode)):
                dt, dv = re.match(r"([^:]+)?(:.*)?", v).groups()

                if value is _NOT_SET_ and not dv:
                    raise ValueError("value for `%s` is not set." % k)

                if value is _NOT_SET_:
                    value = dv[1:]

                if dt:
                    # noinspection PyCallingNonCallable
                    value = _MAPPING[dt](value)
            else:
                if value is _NOT_SET_:
                    raise ValueError("value for `%s` is not set." % k)

            setattr(cls, k, value)

    @classmethod
    def load_config_file(cls, config_file):
        with open(config_file, 'r') as f:
            config = json.loads(f.read())

        cls.load_config(config)


def test():
    class C(BaseConfig):
        # Define your attributes here first.

        # Value `None` means MUST set in config.
        DEBUG = None

        # Use value `[TYPE][:DEFAULT]` to indicate its type and default value.
        DEFAULT_TYPE_VALUE = "int:6"

        # Only set default type
        DEFAULT_TYPE = "str"
        # Only set default value
        DEFAULT_VALUE = ":222"


        # Use nametuple to define 1-level attributes
        SOME = namedtuple("Some", 'x y')

        # Use inner class to define multi-level attributes
        class L1(BaseConfig):
            class L2(BaseConfig):
                V = None

    config = {
        'DEBUG': True,

        'DEFAULT_TYPE': 'hello',

        'SOME': {
            'x': 1,
            'y': 2,
        },
        'L1': {
            'L2': {
                'V': 123
            }
        }
    }
    C.load_config(config)

    assert C.SOME.y == config['SOME']['y'], C.__dict__
    assert C.L1.L2.V == config['L1']['L2']['V'], C.__dict__
    assert C.DEFAULT_TYPE_VALUE == 6
    assert C.DEFAULT_TYPE == 'hello'
    assert C.DEFAULT_VALUE == '222'

if __name__ == '__main__':
    test()