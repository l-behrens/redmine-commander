#!/usr/bin/env python
from pprint import pprint
from subprocess import call
from dateutil import parser
from dateutil import relativedelta
from datetime import datetime
import hashlib
import operator
import shelve
import rofi
import argparse
import webbrowser
import json
import logging
import redminelib
import requests
import sys
import os
import time
import ast


show = [
       "/issues mine        - show issues assigned to me",
       "/issues open  \t    - show all issues",
       "/issues all         - show open issues",
       "/projects      \t    - show all projects",
       "/time add      \t    - issue_id comment time_in_h",
       "/time show     \t    - issue_id"
]


r=rofi.Rofi(width=80)

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

def timedelta_to_int(t):
    return int("{:04d}{:04d}{:04d}{:04d}{:04d}{:04d}{:04d}{:04d}".format(t.years,
                                t.months,
                                t.weeks,
                                t.days,
                                t.hours,
                                t.minutes,
                                t.seconds,
                                t.microseconds))

def fetch_all_issues():
    fltr = [ "status_id=*", "limit=100" ]

    issues=[]
    for index, page in enumerate(pager(base_url, apikey, *fltr, cert=cert)):
        i = json.loads(page.text)['issues']
        issues.extend(sorted(i, key=lambda k: k['id']))
        if len(i)<100:
            break

    print(f_src)
    with shelve.open(f_src) as db:
        db['issues'] = issues

    return len(issues)


def get_issues(j='', **kwargs):
       print(f_src)
       if not j:
           with shelve.open(f_src) as db:
                issues = db['issues']
       else:
           issues = sorted(j["issues"], key=lambda k: k['id'])
       tmp={}
       for key, value in kwargs.items():
           issues=[issue for issue in issues if str(value) in str(issue)]
       for index, issue in enumerate(reversed(issues)):
           updated_on=parser.parse(issue['updated_on']).replace(tzinfo=None)
           now = datetime.now()
           t_delta=relativedelta.relativedelta(now, updated_on)
           t_int=timedelta_to_int(t_delta)
           ago="weeks ago"
           if (t_delta.weeks==0 and t_delta.months==0 and t_delta.years==0):
               if (t_delta.days==0):
                   if (t_delta.hours==0):
                       ago="%s minutes ago" % t_delta.minutes
                   else:
                       ago="%s hours ago" % t_delta.hours
               else:
                   ago="%s days ago" % t_delta.days
           project=issue["project"]["name"].lower()
           subject=issue["subject"].lower()
           t_id=issue["id"]
           tmp[t_int]=[t_id, '{:8s} {:30.25s} {:85.80s} {:>20s}'.format(
               str(t_id).strip(),
               str(project[:25]).strip().ljust(25),
               str(subject[:80]).strip(),
               ago)]
       return tmp

def get_projects(j):
       projects = sorted(j["projects"], key=lambda k: k['id'])
       tmp={}
       for index, project in enumerate(reversed(projects)):
          name = project["name"].lower()
          p_id = str(project["id"])
          if len(p_id) < 2:
              p_id+='\t'
          tmp[index]=[p_id, 'P {:<6}\t{:<22}'.format(p_id, name)]
       return tmp

def print_projects(j):
       projects = sorted(j["projects"], key=lambda k: k['id'])
       for project in reversed(projects):
          name = project["name"]
          p_id = str(project["id"])
          if len(p_id) < 2:
              p_id+='\t'
          print('P {:<6}\t{:<22}'.format(p_id, name))

def print_time_entries(j):
       for time_entry in reversed(time_entries):
          name = project["name"]
          p_id = str(project["id"])
          if len(p_id) < 2:
              p_id+='\t'
          print('{:<6}\t{:<22}'.format(p_id, name))

def pre_checks(cert):
    if not os.path.isfile(cert[0]):
        logging.log(logging.ERROR, "missing cert.crt file")
        sys.exit(1)
    elif not os.path.isfile(cert[1]):
        logging.log(logging.ERROR, "missing key.pem file")
        sys.exit(1)

def comment_menu(t_id):
    ret = req(base_url, apikey, "issues.json", "issue_id=%s" % t_id, cert=cert)
    items=get_issues(json.loads(ret.text))
    prompt="comments"
    print(items)
    opt, key=r.select(prompt,  items)

def ticket_menu(items):
    url = "%s/issues" % (base_url)
    prompt="tickets"

    while True:
        opt, key=r.select(prompt,  [items[i][1] for i in sorted(items.keys())],
                           key1=('Alt+u', "scroll the comments"),
                           key2=('Alt+i', "post a comment"),
                           key3=('Alt+o', "open in browser"),
                           key4=('Alt+p', "book working hours"),
                       message="Ticket Options are:")

        t_id=items[sorted(items)[opt]][0]
        if key is -1:
            return
        if key is 0:
            print("open in webbrowser")
            url = "%s/issues/%s" % (base_url, t_id)
            webbrowser.open_new_tab(url)
        if key==1:
            comment_menu(t_id)
            print("see the comments")
        if key==2:
            print("post a comment")
        if key==3:
            print("open in webbrowser")
            url = "%s/issues/%s" % (base_url, t_id)
            webbrowser.open_new_tab(url)
        if key==4:
            print("book working hours")


def pager(r_type, *args, cert=False):
    c=0
    while True:
        try:
            ret = req(base_url, apikey, "issues.json", *args, 'offset=%s' % c, cert=cert)
            yield ret
            c+=100
        except Exception as e:
            print("paging error %s" % e)
            pass

def menu():
    opt=-1
    quit=0
    prompt="menu"
    while True:
        opt, key=r.select(prompt=prompt, options=show,
                          message="welcome to the redmine commander version: 1.0.4",
                          key1=('Alt+u', "show my tickets"),
                          key2=('Alt+i', "show open tickets"),
                          key3=('Alt+o', "show all tickets"),
                          key4=('Alt+p', "show all projects"),
                          key5=('Alt+r', "refresh"),
                          key6=('Alt+e', "make a comment"),
                          key7=('Alt+w', "show my protocol"),
                          key8=('Alt+q', "quit"),
                          key9=('Alt+t', "switch theme")
                          )
        if key==-1:
            sys.exit(0)
        if key==1:

            items = get_issues(assined_to='Lars Behrens')
#            print('show all my')
#            fltr=[ "assigned_to_id=me", "status_id=open", "limit=100", "sort=updated_on"]
#            items={}
#
#            for index, page in enumerate(pager(base_url, apikey, *fltr, cert=cert)):
#                i = get_issues(json.loads(page.text))
#                items={**items, **i}
#                if len(i)<100:
#                    break
            ticket_menu(items)

        if key==2:
            fltr = ["status_id=open", "limit=100"]

            items={}
            for index, page in enumerate(pager(base_url, apikey, *fltr, cert=cert)):
                i = get_issues(json.loads(page.text))
                items={**items, **i}
                if len(i)<100:
                    break
            ticket_menu(items)

        if key==3:
            print('show all tickets')

            items = get_issues()
            ticket_menu(items)
        if key==4:
            print('show all projects')
        if key==5:
            print('refresh')
            r.status('sure about that? Press any key to continue, ESC to abort')
            tickets=fetch_all_issues()
            r.status('refreshing index done: %s in total! Any key to return' % tickets)
            time.sleep(3)
        if key==6:
            print('make a comment')
        if key==7:
            print('show my protocol')
            ret = req(base_url, apikey, "time_entries.json", "limit=500", "user_id=me", cert=cert)
            items=json.loads(ret.text)
            print(items)
        if key==8:
            print('bye...')
            sys.exit(0)
        if key==9:
            call('rofi-theme-selector')
        opt=-1

def sub_menu(prompt, items, base_url):
    quit=0
    while quit is not -1:
        opt, quit=r.select(prompt,  [i[1] for i in items.values()], message="press Enter to open a ticket in your Browser")
        url = "%s/%s" % (base_url, items[opt][0])
        if opt is -1:
            break
        webbrowser.open_new_tab(url)

def parse_args():
    parser = argparse.ArgumentParser(description='Redmine Commander')
    parser.add_argument('--cert_dir', '-c', type=str, action='store', required=False,
                        help='key.pem and cert.crt must be present in the directory')
    parser.add_argument('--url', '-u', type=str, action='store', required=True,
                        help='redmine base url, E.g. https://project.solutionstm.eu')
    parser.add_argument('--key', '-k', type=str, action='store', required=True,
                        help='api secret key')
    return parser.parse_args()

def run():
    global cert
    global apikey
    global base_url
    global f_src

    args=parse_args()
    if not args.cert_dir:
        cert=None
    else:
        cert_dir=args.cert_dir
        cert=(os.path.join(cert_dir, 'cert.crt'), os.path.join(cert_dir, 'key.pem'))
        pre_checks(cert)

    base_url=args.url
    base_url_sha224=hashlib.sha224(base_url.encode('utf-8'))

    f_src='/'.join(['/tmp', base_url_sha224.hexdigest(), 'issues.db'])
    apikey=args.key
    menu()

if __name__ == "__main__":
    global cert
    global apikey
    global base_url
    global f_src

    args=parse_args()
    if not args.cert_dir:
        cert=None
    else:
        cert_dir=args.cert_dir
        cert=(os.path.join(cert_dir, 'cert.crt'), os.path.join(cert_dir, 'key.pem'))
        pre_checks(cert)
    base_url=args.url
    base_url_sha224=hashlib.sha224(base_url.encode('utf-8'))

    f_src='/'.join(['/tmp', base_url_sha224.hexdigest(), 'issues.db'])

    apikey=args.key

#    fetch_all_issues()
    run()
