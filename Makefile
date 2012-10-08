VERSION := $(shell git describe | sed s/v//)

all: ploddle_$(VERSION)_all.deb ploddle_$(VERSION).noarch.rpm

ploddle_$(VERSION)_all.deb: ploddle/* ploddle-*
	mkdir -p fs/usr/bin/
	cp ploddle-collector ploddle-web ploddle-top ploddle-example fs/usr/bin/
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

.venv:
	virtualenv .venv
	.venv/bin/pip install nose coverage pep8 requests pymongo

pep8:
	.venv/bin/pep8 --max-line-length 150 ploddle | tee .pep8.out

test: .venv pep8
	.venv/bin/nosetests -v --with-doctest ploddle --with-coverage --cover-package=ploddle
