#!/usr/bin/env python

from logging.handlers import SysLogHandler
import logging
import sys
import json
import os


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
        if d["exc_info"]:
            d["exc_info"] = str(d["exc_info"])

        return "ploddle:json:"+json.dumps(d)


class PloddleHandler(SysLogHandler):
    def __init__(self, addr='localhost', port=5141, daemonName=None):
        if not daemonName:
            daemonName = os.path.basename(sys.argv[0])
        logging.handlers.SysLogHandler.__init__(self, address=(addr, port))
        self.setFormatter(PloddleFormatter(daemonName))