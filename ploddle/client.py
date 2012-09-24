#!/usr/bin/env python

import sys
import requests
import time
import json


filters = {
    "daemon": "sshd",
    "since": "",
}


def handle_row(row):
    print row
    filters["since"] = row["timestamp"]


def get_data():
    r = requests.get("http://localhost:5140/api/messages.json", params=filters)
    for row in r.json["messages"]:
        handle_row(row)


def main(args):
    try:
        while True:
            get_data()
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    sys.exit(main(sys.argv))
