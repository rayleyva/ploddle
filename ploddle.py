#!/usr/bin/python

from logging.handlers import SysLogHandler
import logging
import sys
import json


class PloddleFormatter(logging.Formatter):
    def __init__(self, daemonName):
        logging.Formatter.__init__(self)
        self.daemonName = daemonName

    def format(self, record):
        attrs = [
            #"asctime",
            "created",
            "exc_info",
            "filename",
            "funcName",
            #"levelnam",
            "levelno",
            "lineno",
            "module",
            "msecs",
            #"message",
            "name",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "thread",
            "threadName",
        ]

        d = {}
        for a in attrs:
            d[a] = getattr(record, a)
        d["daemon"] = self.daemonName
        d["message"] = record.msg % record.args

        return "ploddle:json:"+json.dumps(d)


class PloddleHandler(SysLogHandler):
    def __init__(self, addr, port, daemonName=None):
        if not daemonName:
            daemonName = sys.argv[0]
        logging.handlers.SysLogHandler.__init__(self, address=(addr, port))
        self.setFormatter(PloddleFormatter(daemonName))


if __name__ == "__main__":
    my_logger = logging.getLogger('ploddle.demo')
    my_logger.setLevel(logging.DEBUG)
    my_logger.addHandler(PloddleHandler('localhost', 5141))

    my_logger.debug('this is debug')
    my_logger.critical('this is critical')
