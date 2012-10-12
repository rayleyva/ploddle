#!/usr/bin/env python

import re
import sys
import syslog
import socket
import json

adblevels = {
    "F": syslog.LOG_ERR,  # syslog.LOG_EMERG,
    "A": syslog.LOG_ERR,  # syslog.LOG_ALERT,
    "C": syslog.LOG_ERR,  # syslog.LOG_CRIT,
    "E": syslog.LOG_ERR,
    "W": syslog.LOG_WARNING,
    "V": syslog.LOG_NOTICE,
    "I": syslog.LOG_INFO,
    "D": syslog.LOG_DEBUG
}

pattern = re.compile("(.)/(.*?)\(\s*(\d+)\):\s*(.*)")


def pipe(name, stream, sock, target):
    for line in sys.stdin:
        matches = pattern.match(line.strip())
        if matches:
            adblevel = matches.group(1)
            daemon = matches.group(2)
            pid = matches.group(3)
            message = matches.group(4)
            
            facility = syslog.LOG_USER
            severity = adblevels[adblevel]
            priority = facility << 3 | severity

            packet = {
                "adblevel": adblevel,
                "hostname": name or "android",
                "pid": pid,
                "daemon": daemon,
                "message": message
            }
            sock.sendto("<%d>ploddle:json:%s\n" % (priority, json.dumps(packet)), target)
        else:
            print "Error, bad line: ", line


def main():
    name = None
    target = ("127.0.0.1", 5141)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    pipe(name, sys.stdin, sock, target)
