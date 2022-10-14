#!/usr/bin/env python

import os

from setuptools import find_packages, setup

from remote_models import __version__


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# the setup
setup(
    name="remote_models",
    version=__version__,
    description="Library to access remote models via REST API",
    url="https://github.com/noviscient/remote_models",
    author="denisvolokh",
    author_email="denis.volokh@noviscient.com",
    license="MIT",
    keywords="models remote rest api",
    packages=find_packages(exclude=("docs", "tests", "env", "index.py")),
    include_package_data=True,
    install_requires=[],
    extras_require={
        "dev": [],
        "docs": [],
        "testing": [],
    },
    classifiers=[],
)
