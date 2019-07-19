#!/usr/bin/env python
import logging
import subprocess
import json
import os
import webbrowser
import requests

def timedelta_to_int(t):
    return int("{:04d}{:04d}{:04d}{:04d}{:04d}{:04d}{:04d}{:04d}".format(t.years,
                                t.months,
                                t.weeks,
                                t.days,
                                t.hours,
                                t.minutes,
                                t.seconds,
                                t.microseconds))

def pager(base_url, apikey, *args, cert=False, what="issues.json"):
    c=0
#    if what is "time_entries.json":
    while True:
        try:
            ret = req(base_url, apikey, what, *args, 'offset=%s' % c, cert=cert)
            yield ret
            c+=100
        except Exception as e:
            print("paging error %s" % e)
            pass


def req(base_url, key, r_type, *kwargs, cert=False):
    try:
        f_req = '&'.join(['key=%s' % key, *kwargs])
        f_req = os.path.join(base_url, "%s?%s" % (r_type,f_req))
        print(f_req)
        if cert:
            return requests.get(f_req, cert=cert)
        else:
            return requests.get(f_req)
    except Exception as e:
        logging.log(logging.ERROR, "REST Call failed\n%s" %  e)

def open_in_browser(pattern, *args):
    print(str(pattern) % args)
    webbrowser.open_new_tab(str(pattern) % args)

def switch_theme():
    print("open theme selector")
    subprocess.call("/bin/rofi-theme-selector")
