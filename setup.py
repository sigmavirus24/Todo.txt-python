#!/usr/bin/env python

import sys
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] in ("submit", "publish"):
    os.system("python setup.py sdist upload")
    sys.exit()

packages = []
requires = []

setup(
    name="todo.py",
    version="0.3-beta-3",
    description="Python version of Gina Trapani's popular bash script.",
    long_description="\n\n".join([open("README.rst").read(), 
        open("HISTORY.rst").read()]),
    author="graffatcolmingov",
    author_email="graffatcolmingov@gmail.com",
    url="https://github.com/sigmavirus24/Todo.txt-python",
    package_data={'': ['LICENSE']},
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Console', 
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: IronPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        ),
    scripts=["todo.py"]
    )
