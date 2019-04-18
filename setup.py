#! /usr/bin/env python
# coding: utf-8

from __future__ import print_function

import os
import sys
from setuptools import setup

pjoin = os.path.join
here = os.path.abspath(os.path.dirname(__file__))

# Get the current package version.
version_ns = {}
with open(pjoin(here, 'version.py')) as f:
    exec(f.read(), {}, version_ns)

setup_args = dict(
    name                    = 'logopy',
    packages                = ['logopy'],
    version                 = version_ns['__version__'],
    description             = """LogoPy: An implementation of the Logo programming language in Python with TK and SVG turtle back ends.""",
    long_description        = "",
    author                  = "Carl (https://github.com/cwaldbieser)",
    author_email            = "cwaldbieser@gmail.com",
    url                     = "https://github.com/cwaldbieser/logopy",
    license                 = "GPLv3",
    platforms               = "Linux, Mac OS X",
    keywords                = ['Logo', 'Turtle', 'SVG',],
    classifiers             = [
        'Intended Audience :: Developers',
        'Programming Language :: Logo',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: Editors :: Vector-Based',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    data_files              = [('.', ['version.py'])],
    scripts                 = ['bin/logopycli.py'],
    include_package_data    = True,
)

# setuptools requirements
if 'setuptools' in sys.modules:
    setup_args['install_requires'] = install_requires = []
    install_requires.append('parsley')
    install_requires.append('attrs')
    install_requires.append('svgwrite')
    install_requires.append('jinja2')

def main():
    setup(**setup_args)

if __name__ == '__main__':
    main()
