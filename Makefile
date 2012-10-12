VERSION := $(shell git describe | sed s/v//)

all: ploddle_$(VERSION)_all.deb ploddle_$(VERSION).noarch.rpm

ploddle_$(VERSION)_all.deb: ploddle/* ploddle-*
	mkdir -p fs/usr/bin/
	cp ploddle-collector ploddle-web ploddle-top fs/usr/bin/
	mkdir -p fs/usr/lib/python2.7/site-packages/
	cp -r ploddle fs/usr/lib/python2.7/site-packages/
	mkdir -p fs/etc/ploddle/
	cp *.conf fs/etc/ploddle/
	mkdir -p fs/DEBIAN/
	echo ================================================ >/dev/null
	echo "Package: ploddle" > fs/DEBIAN/control
	echo "Version: ${VERSION}" >> fs/DEBIAN/control
	echo "Architecture: all" >> fs/DEBIAN/control
	echo "Maintainer: Shish <shish@shishnet.org>" >> fs/DEBIAN/control
	echo "Depends: python-pymongo" >> fs/DEBIAN/control
	echo "Description: a python logging debug thing" >> fs/DEBIAN/control
	echo ================================================ >/dev/null
	fakeroot dpkg -b fs ploddle_${VERSION}_all.deb
	rm -rf fs

ploddle_$(VERSION).noarch.rpm: ploddle/* ploddle-*
	rpmbuild -ba ploddle.spec

test:
	virtualenv .venv
	.venv/bin/python tools/setup.py develop
	.venv/bin/python collector/setup.py develop
	.venv/bin/python web/setup.py develop
	.venv/bin/python logger/setup.py develop
	.venv/bin/pip install pep8 nose coverage
	.venv/bin/pep8 --max-line-length 150 */ploddle/*/*.py || true
	.venv/bin/nosetests -v --with-doctest --with-coverage --cover-package=ploddle */ploddle/*/*.py

install:
	virtualenv .venv
	.venv/bin/python setup_tools.py install
	.venv/bin/python setup_collector.py install
	.venv/bin/python setup_web.py install
	.venv/bin/python setup_logger.py install

eggs:
	python tools/setup.py develop
	python collector/setup.py develop
	python web/setup.py develop
	python logger/setup.py develop

clean:
	git clean -fdx
