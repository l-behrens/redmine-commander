#!/usr/bin/env python
from pprint import pprint
#from joblib import Parallel, delayed
import rofi
import argparse
import webbrowser
import json
import logging
import redminelib
import requests
import sys
import os

show = [
       "Redmine Commander!",
       "/issues mine                - show issues assigned to me",
       "/issues all    \t            - show all issues",
       "/projects      \t            - show all projects",
       "/time add      \t            - issue_id comment time_in_h",
       "/time show     \t            - issue_id"
]


r=rofi.Rofi(width=80)

def req(base_url, key, r_type, *kwargs, cert=False):
    try:
        f_req = '&'.join(['key=%s' % key, *kwargs])
        f_req = os.path.join(base_url, "%s?%s" % (r_type,f_req))
        if cert:
            return requests.get(f_req, cert=cert)
        else:
            return requests.get(f_req)
    except Exception as e:
        logging.log(logging.ERROR, "REST Call failed\n%s" %  e)

def get_issues(j):
       issues = sorted(j["issues"], key=lambda k: k['id'])
       tmp={}
       for index, issue in enumerate(reversed(issues)):
           project=issue["project"]["name"]
           subject=issue["subject"]
           if len(project) < 20:
               project+='\t'
           t_id=issue["id"]
           tmp[index]=[t_id, 'I {:<6}\t{:<22}\t{:>10}'.format(t_id, project[:20], subject)]
       return tmp

def get_projects(j):
       projects = sorted(j["projects"], key=lambda k: k['id'])
       tmp={}
       for index, project in enumerate(reversed(projects)):
          name = project["name"]
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

def menu(base_url, apikey, cert, options):
    opt=-1
    quit=0
    prompt="menu"
    while opt is -1:
        if quit is -1:
            break
        opt, quit=r.select(prompt, show)
        if not opt in options.keys():
            opt=-1
            prompt="not implemented yet!"
        elif opt is 1:
            ret = req(base_url, apikey, "issues.json", "assigned_to_id=me", "status_id=open", "limit=100", cert=cert)
            items=get_issues(json.loads(ret.text))
            url = "%s/issues" % (base_url)
            prompt=options[opt][0]
            sub_menu(prompt, items, url)
        elif opt is 2:
            ret = req(base_url, apikey,  "issues.json", "status_id=open", "limit=500", cert=cert)
            items=get_issues(json.loads(ret.text))
            url = "%s/issues" % (base_url)
            prompt=options[opt][0]
            sub_menu(prompt, items, url)
        elif opt is 3:
            ret = req(base_url, apikey,  "projects.json", "status_id=open", "limit=500", cert=cert)
            items=get_projects(json.loads(ret.text))
            url = "%s/projects" % (base_url)
            prompt=options[opt][0]
            sub_menu(prompt, items, url)

        opt=-1

def sub_menu(prompt, items, base_url):
    quit=0
    while quit is not -1:
        opt, quit=r.select(prompt, [i[1] for i in items.values()])
        url = "%s/%s" % (base_url, items[opt][0])
        if opt is -1:
            break
        webbrowser.open_new_tab(url)

def parse_args():
    parser = argparse.ArgumentParser(description='Redmine Commander')
    parser.add_argument('--cert_dir', '-c', type=str, action='store', required=True,
                        help='key.pem and cert.crt must be present in the directory')
    parser.add_argument('--url', '-u', type=str, action='store', required=True,
                        help='redmine base url, E.g. https://project.solutionstm.eu')
    parser.add_argument('--key', '-k', type=str, action='store', required=True,
                        help='api secret key')
    return parser.parse_args()

def run():
    args=parse_args()
    cert_dir=args.cert_dir
    cert=(os.path.join(cert_dir, 'cert.crt'), os.path.join(cert_dir, 'key.pem'))
    base_url=args.url
    apikey=args.key

    options={
        1: ["issues mine", get_issues],
        2: ["issues all", get_issues],
        3: ["projects all", get_issues],
        5: ["time records", get_issues]
    }

    pre_checks(cert)
    menu(base_url, apikey, cert, options)


