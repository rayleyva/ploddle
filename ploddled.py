#!/usr/bin/python

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pymongo import Connection

from ConfigParser import SafeConfigParser
import logging
import sys
import re
import threading
import json
import datetime
from socket import *


#######################################################################
# The daemon part
#######################################################################

def get_logger(config):
    try:
        logging.basicConfig(
                level=logging.DEBUG,
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
        logging.info("Successfully bound to port %s:%d" % (host, port))
        return sock
    except Exception:
        logging.exception("Error binding to socket:")


class PloddleViewer(threading.Thread):
    def __init__(self, config_file):
        threading.Thread.__init__(self, name="Viewer")

        config = Configurator()
        config.add_static_view(name='static', path='static/')

        config.add_route('index', '/')
        config.add_view(self.index, route_name='index', renderer='ploddle:templates/index.mako')

        config.add_route('api_messages', '/api/messages.json')
        config.add_view(self.api_messages, route_name='api_messages', renderer='json')

        config.add_route('api_hosts', '/api/hosts.json')
        config.add_view(self.api_hosts, route_name='api_hosts', renderer='json')

        config.add_route('api_daemons', '/api/daemons.json')
        config.add_view(self.api_daemons, route_name='api_daemons', renderer='json')

        self.database = get_database(config_file)
        self.server = make_server('0.0.0.0', 5140, config.make_wsgi_app())

    def index(self, request):
        return dict()

    def api_messages(self, request):
        coll = self.database.entries

        filters = {}
        if request.GET.get("host"):
            filters["host"] = request.GET.get("host")
        if request.GET.get("daemon"):
            filters["daemon"] = request.GET.get("daemon")

        page_size = 50
        page = int(request.GET.get("page", 1)) - 1
        #if request.GET.get("message"):
        #    w.append("message ILIKE %s")
        #    p.append("%"+request.GET.get("message")+"%")

        raw_messages = list(coll.find(filters).sort("timestamp").skip(page*page_size).limit(page_size))
        pages = coll.find(filters).count() / page_size

        safe_messages = []
        for m in raw_messages:
            doc = {}
            for f in m:
                if f[0] == "_":
                    pass
                elif f == "timestamp":
                    doc[f] = str(m[f])[:16]
                else:
                    doc[f] = m[f]
            safe_messages.append(doc)
        return {
            "page": page,
            "pages": pages,
            "messages": safe_messages,
        }

    def api_hosts(self, request):
        coll = self.database.entries
        return coll.distinct("host")

    def api_daemons(self, request):
        coll = self.database.entries
        return coll.distinct("daemon")

    def run(self):
        logging.info("Running viewer")
        self.server.serve_forever()


class PloddleCollector(threading.Thread):
    def __init__(self, config):
        threading.Thread.__init__(self, name="Collector")

        self.socket = get_socket(config)
        self.database = get_database(config)

    def run(self):
        logging.info("Running collector")
        pattern_std = re.compile("([^:\[]+)(?:\[\d+\])?: (.*)")
        coll = self.database.entries

        while True:
            data, (host, _port) = self.socket.recvfrom(1024)
            logging.debug("Got packet: %s" % data)

            try:
                angle = data.index(">")
                priority = int(data[1:angle])
                therest  = data[angle+1:]

                # some syslog daemons send RFC3164 compliant headers,
                # some only send priority and message
                if therest.split()[0] in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
                    (_month, _day, _timestamp, _hostname, message) = therest.split(" ", 4)
                else:
                    message = therest

                priority = int(priority)
                serverity = priority & 0x07
                facility = priority >> 3
            except Exception:
                logging.exception("Error parsing packet from %s: %s " % (str(host), str(data)))
                continue

            doc = {
                "host": host,
                "serverity": serverity,
                "facility": facility,
                "message": message,
                "timestamp": datetime.datetime.utcnow(),
            }

            if message.startswith("ploddle:json:"):
                _ploddle, _json, data = message.split(":", 2)
                logging.debug("Found json data: "+data)
                doc.update(json.loads(data[:-1]))
            elif pattern_std.match(message):
                match_std = pattern_std.match(message)
                doc["daemon"] = match_std.group(1)
                doc["message"] = match_std.group(2)

            from pprint import pprint
            print "inserting"
            pprint(doc)
            coll.insert(doc)


def main(args):
    config = SafeConfigParser()
    config.read("ploddled.conf")

    get_logger(config)

    viewer = PloddleViewer(config)
    viewer.daemon = True
    viewer.start()

    collector = PloddleCollector(config)
    collector.daemon = True
    collector.run()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
