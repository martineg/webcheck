#! /usr/bin/env python

import httplib
import time

user_agent = 'webcheck.py'

def check(host, url="/", ip=None, debuglevel=0):
        if not ip:
                ip = host
	headers = {'Host' : host, 'User-agent' : user_agent}
        h = httplib.HTTPConnection(ip)
        h.set_debuglevel(debuglevel)
        h.request("GET", url, headers=headers)
        r = h.getresponse()
        data = r.read()
        h.close()
        return r, data
# check()

def check_t(host, url="/", ip=None, debuglevel=0):
	t0 = time.time()
	r, data = check(host, url, ip, debuglevel)
	t1 = time.time()
	return (r, data, abs(t1-t0))
# check_t()
