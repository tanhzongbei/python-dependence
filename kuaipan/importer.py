# coding:utf8
"""

Author: ilcwd
"""
import logging
import os

_logger = logging.getLogger(__name__)


def import_submodules(package):
    """
    Import all sub-modules inside ``package``.

    Sub-modules are `.py` files, not start with underscore `_`.

    Attentions:

        Can not import sub-packages.
    """
    m = __import__(package)
    current = os.path.dirname(m.__file__)

    if '.' in package:
        apppath = os.path.join(current, *package.split('.')[1:])
    else:
        apppath = current

    submodules = []
    for fname in os.listdir(apppath):
        if not fname.endswith('.py') or fname.startswith('_'):
            continue

        submodules.append(fname[:-3])

    _logger.info('Load modules %s from package `%s`.', submodules, package)
    return __import__(package, fromlist=submodules)


def main():
    import_submodules('kuaipan.utils')


if __name__ == '__main__':
    main()
