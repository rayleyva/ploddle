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

setup(name='ploddle',
      version='0.0',
      description='ploddle',
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='gummy',
      install_requires=requires,
      entry_points="""\
      [console_scripts]
      ploddle-web = ploddle.server.web:main
      ploddle-collector = ploddle.server.collector:main
      ploddle-top = ploddle.client.top:main
      """,
      )
