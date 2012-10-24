import unittest
from ploddle.logger import PloddleFormatter, PloddleHandler

class TestFormatter(unittest.TestCase):
    def testFormatter(self):
        f = PloddleFormatter(hostname="testhost", daemonName="testdaemon")

class TestHandler(unittest.TestCase):
    def testHandler(self):
        h = PloddleHandler('localhost', 5141)
