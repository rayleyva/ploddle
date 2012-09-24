#!/usr/bin/env python

import sys
import requests
from blessings import Terminal
import time
import json


filters = {
    #"daemon": "sshd",
    "since": "",
    "page": -1,
    "longpoll": "on",
}
t = Terminal()
severity_map = [
    t.blink_black_on_red,
    t.blink_black_on_red,
    t.black_on_red,  # critical
    t.red,  # error, fatal
    t.yellow,  # warning
    t.cyan,
    t.green,  # info
    t.white  # debug
]
rows = []
row_format = "%(severity)-1.1s %(host)-15.15s %(daemon)-10.10s %(message)s"
header_data = {
    "severity": "S",
    "host": "Host",
    "daemon": "Daemon",
    "message": "Message"
}


def handle_row(row):
    rows.append(row)
    filters["since"] = row["timestamp"]


def to_width(text):
    return (text + " "*t.width)[:t.width]


def render_header():
    print t.normal + t.clear
    print t.move(0, 0) + t.black_on_white(to_width(row_format % header_data))


def render_rows():
    visible = rows[-t.height+1:-1]
    for n, r in enumerate(visible):
        text = to_width(row_format % r)
        print t.move(n+1, 0) + severity_map[r["severity"]](text)


def render_input():
    pass


def render():
    render_header()
    render_rows()
    render_input()


def get_data():
    r = requests.get("http://localhost:5140/api/messages.json", params=filters)
    if r.json:
        for row in r.json["messages"]:
            handle_row(row)


def main(args):
    try:
        with t.fullscreen():
            while True:
                get_data()
                render()
                time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    sys.exit(main(sys.argv))
