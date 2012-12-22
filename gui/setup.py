from setuptools import setup, find_packages

setup(
    name='ploddle.gui',
    version='0.0',
    description='GUI Ploddle utilities',
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
    ],
    author='Shish',
    author_email='shish+ploddle@shishnet.org',
    url='http://code.shishnet.org/ploddle',
    keywords='web syslog',
    packages=["ploddle.gui"],
    namespace_packages=["ploddle"],
    include_package_data=True,
    zip_safe=True,
    #test_suite='ploddle',
    install_requires=[
        "requests",
    ],
    entry_points="""\
        [console_scripts]
        ploddle-gui = ploddle.gui.main:main
    """,
)
