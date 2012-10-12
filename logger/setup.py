import os

from setuptools import setup, find_packages

setup(
    name='ploddle.logger',
    version='0.0',
    description='a syslog-compatible log collector and browser, with enhancements',
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
    ],
    author='Shish',
    author_email='shish+ploddle@shishnet.org',
    url='http://code.shishnet.org/ploddle',
    keywords='web syslog',
    packages=["ploddle.logger"],
    namespace_packages=["ploddle"],
    zip_safe=True,
)
