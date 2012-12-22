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
	cd tools     && ../.venv/bin/python setup.py develop
	cd collector && ../.venv/bin/python setup.py develop
	cd web       && ../.venv/bin/python setup.py develop
	cd logger    && ../.venv/bin/python setup.py develop
	cd gui       && ../.venv/bin/python setup.py develop
	.venv/bin/pip install pep8 nose coverage
	.venv/bin/pep8 --max-line-length 150 */ploddle/*/*.py || true
	.venv/bin/nosetests -v --with-doctest --with-coverage --cover-package=ploddle */ploddle/*/*.py

install:
	virtualenv .venv
	cd tools     && python setup.py install
	cd collector && python setup.py install
	cd web       && python setup.py install
	cd logger    && python setup.py install
	cd gui       && python setup.py install
	cd ploddle   && python setup.py install

eggs:
	cd tools     && python setup.py sdist
	cd collector && python setup.py sdist
	cd web       && python setup.py sdist
	cd logger    && python setup.py sdist
	cd gui       && python setup.py sdist
	cd ploddle   && python setup.py sdist
	mkdir dist
	mv ./*/dist/* ./dist/

clean:
	git clean -fdx
