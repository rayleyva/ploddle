
from ConfigParser import RawConfigParser
import os

def get_config(name):
    config = RawConfigParser()

    config.add_section("top")
    config.set("top", "row_format", "%(severity)-1.1s %(host)-15.15s %(daemon)-10.10s %(message)s")

    config.read([
        "/etc/ploddle.conf",
        "/etc/ploddle/"+name+".conf",
        os.path.expanduser("~/.config/ploddle.conf"),
        os.path.expanduser("~/.config/ploddle/"+name+".conf")
    ])

    return config
