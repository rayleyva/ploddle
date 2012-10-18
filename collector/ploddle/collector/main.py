#!/usr/bin/env python

from pymongo import Connection

from ConfigParser import SafeConfigParser
import logging
import sys
import re
import threading
import json
import datetime
import os
from pprint import pformat
from socket import socket, gethostbyaddr, AF_INET, SOCK_DGRAM


def get_logger(config):
    try:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)-8s %(message)s',
        )  # filename=config.get("logging", "file"))
        return True
    except Exception, e:
        print "Error starting logger: %s" % e
        return False


def get_database(config):
    try:
        hostname = config.get("database", "hostname")
        #username = config.get("database", "username")
        #password = config.get("database", "password")
        database = config.get("database", "database")
        conn = Connection(hostname, 27017)
        db = conn[database]
        db.entries.ensure_index("timestamp")
        logging.info("Connected to database")
        return db
    except Exception:
        logging.exception("Failed to connect to database:")


def get_socket(config):
    try:
        host = config.get("bind", "host")
        port = config.getint("bind", "port")
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind((host, port))
        logging.info("Successfully bound collector to port %s:%d" % (host, port))
        return sock
    except Exception:
        logging.exception("Error binding to socket:")


def get_hostname(host):
    """
    >>> get_hostname("127.0.0.1")
    'localhost'
    >>> get_hostname("1.2.3.4")
    '1.2.3.4'

    TODO: should do a DNS lookup...
    """
    rdns = "none"
    if rdns == "none":
        return host
    elif rdns == "hosts":
        pass
    elif rdns == "all":
        return gethostbyname(host)[0]
    else:
        # raise exception
        return host


def parse_syslog_packet(data):
    angle = data.index(">")
    priority = int(data[1:angle])
    therest = data[angle + 1:]

    # some syslog daemons send RFC3164 compliant headers,
    # some only send priority and message
    if therest.split()[0] in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
        (_month, _day, _timestamp, _hostname, message) = therest.split(" ", 4)
    else:
        message = therest

    priority = int(priority)
    severity = priority & 0x07
    facility = priority >> 3

    return (severity, facility, message)


class PloddleCollector(threading.Thread):
    def __init__(self, config, database):
        threading.Thread.__init__(self, name="Collector")

        self.socket = get_socket(config)
        self.database = database

    def run(self):
        logging.info("Running collector")
        pattern_std = re.compile("([^:\[]+)(?:\[\d+\])?: (.*)")
        coll = self.database.entries

        while True:
            data, (host, _port) = self.socket.recvfrom(1024)
            logging.debug("Got packet: %s" % data)

            try:
                (severity, facility, message) = parse_syslog_packet(data)
            except Exception:
                logging.exception("Error parsing packet from %s: %s " % (str(host), str(data)))
                continue

            doc = {
                "host": host,
                "severity": severity,
                "facility": facility,
                "message": message,
                "timestamp": datetime.datetime.utcnow(),
            }

            if message.startswith("ploddle:json:"):
                try:
                    _ploddle, _json, data = message.split(":", 2)
                    logging.debug("Found json data: " + data)
                    doc.update(json.loads(data[:-1]))
                except Exception:
                    pass  # message will be logged as a normal message
            elif pattern_std.match(message):
                match_std = pattern_std.match(message)
                doc["daemon"] = match_std.group(1)
                doc["message"] = match_std.group(2).strip()

            if "hostname" not in doc:
                doc["hostname"] = get_hostname(host)

            logging.debug("inserting: " + pformat(doc))
            coll.insert(doc)


def main():
    try:
        config = SafeConfigParser()
        if os.path.exists("ploddled.conf"):
            config.read("ploddled.conf")

        logger = get_logger(config)
        database = get_database(config)

        if logger and database:
            PloddleCollector(config, database).run()
    except KeyboardInterrupt:
        pass
