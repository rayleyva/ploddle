Ploddle
=======

A syslog-compatible log collector, with extra bits:

- support for arbitrary fields by logging JSON
  - comes with a Python logging handler, so you can call logging.info("foo")
    as normal, and that message (with module, line number, etc) will be
	stored in the database
- web interface for searching
- console interface for tailing


Hooking into syslog
===================

/etc/rsyslog.d/forward.conf:
```
*.* @ploddlehost:5141
```


Sending extra data
==================
syslog(
	ploddle:json:{"filename": "foo.c", "linenum": 123, "message": "A test!"}
)
