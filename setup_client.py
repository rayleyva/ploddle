import os

from setuptools import setup, find_packages

setup(
    name='ploddle.client',
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
    packages=["ploddle.client"],
    namespace_packages=["ploddle"],
    include_package_data=True,
    zip_safe=True,
    #test_suite='ploddle',
    install_requires=[
        "requests",
        "blessings",
    ],
    entry_points="""\
        [console_scripts]
        ploddle-top = ploddle.client.top:main
    """,
)
