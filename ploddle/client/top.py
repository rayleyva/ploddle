#!/usr/bin/env python

import sys
import requests
from blessings import Terminal
import time
import os
from ConfigParser import RawConfigParser
import os


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


def get_config(name):
    config = RawConfigParser()

    config.add_section("top")
    config.set("top", "row_format", "%(severity)-1.1s %(host)-15.15s %(daemon)-10.10s %(message)s")

    config.read([
        "/etc/ploddle.conf",
        "/etc/ploddle/" + name + ".conf",
        os.path.expanduser("~/.config/ploddle.conf"),
        os.path.expanduser("~/.config/ploddle/" + name + ".conf")
    ])

    return config


class TitleDict:
    """
    This is what it does:

    >>> x = TitleDict()
    >>> x['waffles']
    'Waffles'
    >>> x['line num']
    'Line Num'

    This is why it's useful:

    >>> fmt = "%(title)10s %(line)5s %(message)s"
    >>> data = {"title": "hello", "line": 12, "message": "this is a table with titles"}
    >>> print fmt % TitleDict(); print fmt % data
         Title  Line Message
         hello    12 this is a table with titles
    """
    def __getitem__(self, x):
        return x.title()


class RowDict:
    """
    >>> fmt = "%(title)10s %(line)5s %(message)s"
    >>> x = RowDict({"message": "it's a row"})
    >>> print fmt % x
             -     - it's a row
    """
    def __init__(self, row):
        self.row = row

    def __getitem__(self, x):
        if x in self.row:
            return self.row[x]
        else:
            return "-"


def handle_row(row):
    rows.append(RowDict(row))
    filters["since"] = row["timestamp"]


def to_width(text):
    return (text + " " * t.width)[:t.width]


def render_header():
    print t.normal + t.clear
    print t.move(0, 0) + t.black_on_white(to_width(row_format % TitleDict()))


def render_rows():
    visible = rows[-t.height + 1:-1]
    for n, r in enumerate(visible):
        text = to_width(row_format % r)
        print t.move(n + 1, 0) + severity_map[r["severity"]](text)


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
        if r.json["messages"]:
            return True
    return False


def main():
    try:
        config = get_config("top")

        global row_format
        row_format = config.get("top", "row_format")

        with t.fullscreen():
            while True:
                if get_data():
                    render()
                time.sleep(1)
    except KeyboardInterrupt:
        pass
