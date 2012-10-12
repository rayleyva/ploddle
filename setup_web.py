import os

from setuptools import setup, find_packages

setup(
    name='ploddle.web',
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
    packages=["ploddle.web"],
    namespace_packages=["ploddle"],
    include_package_data=True,
    zip_safe=True,
    #test_suite='ploddle',
    install_requires=[
        "pymongo",
        "pyramid",
    ],
    entry_points="""\
        [console_scripts]
        ploddle-web = ploddle.server.web:main
    """,
)
