import os

from setuptools import setup, find_packages

requires = [
    "requests",
    "pymongo",
    "blessings",
    "pyramid",
    # testing
    'nose',
    'coverage',
    'pep8',
    ]

setup(name='Ploddle',
      version='0.0',
      description='a syslog-compatible log collector and browser, with enhancements',
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        ],
      author='',
      author_email='',
      url='',
      keywords='web syslog',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      #test_suite='ploddle',
      install_requires=requires,
      entry_points="""\
      [console_scripts]
      ploddle-web = ploddle.server.web:main
      ploddle-collector = ploddle.server.collector:main
      ploddle-top = ploddle.client.top:main
      """,
      )
