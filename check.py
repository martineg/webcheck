#! /usr/bin/env python
#

import threading
import socket
import sqlite3
import time
import logging
from logging.handlers import SMTPHandler
from webcheck import check_t

# setup
warn_timeout = 10
crit_timeout = 30
min_bytes = 1500
ok_codes = [200, 301, 302]
socket.setdefaulttimeout(crit_timeout)
datefmt = "%Y-%m-%d %H:%M"
maillog_sender = "webcheck@martineg.net"
maillog_receivers = [maillog_sender]
maillog_smtpserver = 'localhost'

tests = {'size' : {'test' : "len(data) > min_bytes",
                   'loglevel' : 'error',
                   },
         'status' : {'test' : "r.status in ok_codes",
                     'loglevel' : 'error',
                       },
         'duration' : {'test' : "duration < warn_timeout",
                       'loglevel' : 'warning',
                        },
         'completepage' : {'test' : "'</html>' in data",
                           'loglevel' : 'error',
                           },
         }

# logging
log = logging.getLogger("webcheck")
log.setLevel(logging.DEBUG)
logfmt = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s", datefmt)
filelog = logging.FileHandler("webcheck.log", "w")
filelog.setLevel(logging.INFO)
filelog.setFormatter(logfmt)
maillog = SMTPHandler(maillog_smtpserver, maillog_sender, maillog_receivers, "webcheck error")
maillog.setLevel(logging.ERROR)
maillog.setFormatter(logfmt)
log.addHandler(filelog)
log.addHandler(maillog)

dbc = sqlite3.connect("checks.db")
dbc.row_factory = sqlite3.Row
cur = dbc.cursor()

class WebCheck(threading.Thread):
    def __init__(self, site, uri):
        threading.Thread.__init__(self)
        self.site = site
        self.uri = uri
        self.setName("%s%s" % (site, uri))
        self.timestamp = time.time()
        self.status = ()
    # __init__()
    
    def run(self):
        log.debug("%s starting" % (self.getName()))
        try:
            self.status = check_t(self.site, self.uri)
        except socket.timeout:
            log.error("%s did not respond within %d seconds" % (self.site, crit_timeout))
        except socket.error, d:
            log.warning("Error reading from %s: %s" % (self.site, d))
        else:
            r, data, duration = self.status
            for tname, t in tests.items():
                if not eval(t["test"]):
                    l = eval("log.%s" % (t["loglevel"]))
                    l("%s failed test: %s" % (self.site, tname))
        finally:
            log.debug("%s done" % (self.getName()))
    # run()
# WebCheck

log.info("Starting checks")
running_checks = []

# fetch sites
sql = ("SELECT hostname, uri FROM site")
sites = { r["hostname"] : r["uri"] or "/" for r in cur.execute(sql) }

# startup
for site, uri in sites.items():
    cur_check = WebCheck(site, uri)
    cur_check.start()
    running_checks.append(cur_check)

# fetch results
while running_checks:
    finished_checks =   [ t for t in running_checks if not t.isAlive() ]
    for c in finished_checks:
        log.debug("%s finished" % c.getName())
        running_checks.remove(c)
        if not c.status:
            insert = "INSERT INTO webcheck(timestamp, site) VALUES (?, ?)"
            params = (c.timestamp, c.site)
        else:
            r, data, duration = c.status
            insert = "INSERT INTO webcheck(timestamp, site, duration, result, size) VALUES (?, ?, ?, ?, ?)"
            params = (c.timestamp, c.site, duration, "%d %s" % (r.status, r.reason), len(data))
        cur.execute(insert, params)
        dbc.commit()
log.info("Finished checks")
cur.close()
