# coding:utf8
"""
Created on Jun 18, 2014

@author: ilcwd
"""

import os
from setuptools import setup, find_packages


_current_dir = os.path.dirname(__file__)
install_requires = [ i for i in open(os.path.join(_current_dir, 'requirements.txt')).readlines() if not i.startswith(('-','#','\n'))]
VERSION = open(os.path.join(_current_dir, 'VERSION')).read().strip()

setup(
    name='kuaipan-python',
    description="Utilities for kuaipan",
    long_description=open(os.path.join(_current_dir, 'README.md')).read(),
    version=VERSION,
    packages=find_packages(exclude=['examples', 'tests']),
    install_requires=install_requires,
    author="Ilcwd",
    author_email="ilcwd23@gmail.com",
    license="No License",
    platforms=['any'],
    url="",
    classifiers=["Intended Audience :: Developers",
                 "Programming Language :: Python",
                 "Topic :: Database",
                 "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    test_suite='nose.collector',
    tests_require=['nose', 'mock'],
)
