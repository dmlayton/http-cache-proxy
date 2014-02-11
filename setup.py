#!/usr/bin/env python

from setuptools import setup

VERSION = "0.0.4"

base_url = "http://github.com/dlayton/http-cache-proxy/"

name = 'http_cache'

setup(
    name=name,
    packages=[name],
    provides=[name],
    description='WSGI middleware to add HTTP Caching',
    version=VERSION,
    author="David Layton",
    author_email="dmlayton@gmail.com",
    url=base_url,
    #long_description=open("README.rst").read(),
    install_requires=['WebOb==1.3.1'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Operating System :: POSIX',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)