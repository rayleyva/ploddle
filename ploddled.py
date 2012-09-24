#!/usr/bin/env python

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pymongo import Connection, DESCENDING

from ConfigParser import SafeConfigParser
import logging
import sys
import re
import threading
import json
import datetime
from pprint import pformat
from socket import *


#######################################################################
# The daemon part
#######################################################################

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


class PloddleViewer(threading.Thread):
    def __init__(self, config_file, database):
        threading.Thread.__init__(self, name="Viewer")

        self.database = database
        
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

        host = config_file.get("viewer", "host")
        port = config_file.getint("viewer", "port")
        self.server = make_server(host, port, config.make_wsgi_app())
        logging.info("Successfully bound viewer to port %s:%d" % (host, port))

    def index(self, request):
        return dict()

    def api_messages(self, request):
        coll = self.database.entries

        filters = {}
        if request.GET.get("host"):
            filters["host"] = request.GET.get("host")
        if request.GET.get("timestamp"):
            date = datetime.datetime.strptime(request.GET.get("timestamp"), "%Y-%m-%d")
            print date
            filters["timestamp"] = {
                "$gte": date,
                "$lt": date + datetime.timedelta(days=1)
            }
        if request.GET.get("daemon"):
            filters["daemon"] = request.GET.get("daemon")
        if request.GET.get("since"):
            filters["timestamp"] = {
                "$gt": datetime.datetime.strptime(request.GET.get("since"), "%Y-%m-%d %H:%M:%S.%f")
            }
        if request.GET.get("severity"):
            filters["severity"] = {"$lte": int(request.GET.get("severity"))}

        page_size = 5000
        page = int(request.GET.get("page", 1)) - 1
        #if request.GET.get("message"):
        #    w.append("message ILIKE %s")
        #    p.append("%"+request.GET.get("message")+"%")

        if page >= 0:
            raw_messages = list(coll.find(filters).sort("timestamp").skip(page*page_size).limit(page_size))
            pages = coll.find(filters).count() / page_size
        else:
            raw_messages = list(coll.find(filters).sort("timestamp", DESCENDING).limit(page_size))
            raw_messages.reverse()
            pages = -1

        safe_messages = []
        for m in raw_messages:
            doc = {}
            for f in m:
                if f[0] == "_":
                    pass
                elif f == "timestamp":
                    doc[f] = str(m[f])
                else:
                    doc[f] = m[f]
            safe_messages.append(doc)
        return {
            "page": page + 1,
            "pages": pages + 1,
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
                severity = priority & 0x07
                facility = priority >> 3
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
                    logging.debug("Found json data: "+data)
                    doc.update(json.loads(data[:-1]))
                except Exception:
                    pass  # message will be logged as a normal message
            elif pattern_std.match(message):
                match_std = pattern_std.match(message)
                doc["daemon"] = match_std.group(1)
                doc["message"] = match_std.group(2)

            logging.debug("inserting: "+pformat(doc))
            coll.insert(doc)


def main(args):
    config = SafeConfigParser()
    config.read("ploddled.conf")

    logger = get_logger(config)
    database = get_database(config)

    if logger and database:
        viewer = PloddleViewer(config, database)
        viewer.daemon = True
    
        collector = PloddleCollector(config, database)
        collector.daemon = True
        
        viewer.start()
        collector.run()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
