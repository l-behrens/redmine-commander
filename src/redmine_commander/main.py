#!/usr/bin/env python
from pprint import pprint
from subprocess import call
from redmine_commander.redmine_data import *
from redmine_commander.config import configmap
from redmine_commander.config import services
from redmine_commander.confluence_data import fetch_confluence_documents
from redmine_commander.confluence_data import get_confluence_documents
from redmine_commander.confluence_data import preview_document
from redmine_commander.confluence_data import confluence_open_in_browser
import datetime
import redmine_commander.data as data
import redmine_commander.custom_rofi as custom_rofi
import operator
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

r=custom_rofi.rofi_redmine(width=90, lines=30)
conf_file='/'.join([
    os.getenv('HOME'),
    '.config',
    'redmine_commander',
    'settings.db'
   ])

# reads configmap and executes associated methods. 
# this is a template parser for rofi program calls
def parse_config(domain="main", view="default", t_id=None, on_prev="main"):
    if not configmap[domain]:
        return
    v=configmap[domain]
    options=eval(v['view'][view])
    options=[options[i] for i in sorted(options.keys())]
    opts=[(key, opt[0]) for key, opt in v["options"].items()]
    key,value=r.custom_select(v["prompt"],
                              [item[1] for item in options],
                              *opts,
                              message=v["message"])

    for i, o in enumerate(opts):
        if int(value) == i+1:
            t_id=[item[0] for item in options][key]
            eval(v['options'][o[0]][1])

    if value==-1:
        if domain is "main":
            sys.exit(0)
        else:
            parse_config(t_id=t_id, domain=on_prev)

    parse_config(domain=domain, view=view, t_id=t_id, on_prev=on_prev)

def openi_open_in_browser(tid):
    webbrowser.open_new_tab(str(services[tid]))


def greeting():
    return {k:(k,v) for k,v in enumerate(services)}

def pre_checks(cert):
    if not os.path.isfile(cert[0]):
        logging.log(logging.ERROR, "missing cert.crt file")
        sys.exit(1)
    elif not os.path.isfile(cert[1]):
        logging.log(logging.ERROR, "missing key.pem file")
        sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description='Redmine Commander')
    parser.add_argument('--cert_dir', '-c', type=str, action='store', required=False,
                        help='key.pem and cert.crt must be present in the directory')
    parser.add_argument('--url', '-u', type=str, action='store', required=True,
                        help='redmine base url, E.g. https://project.solutionstm.eu')
    parser.add_argument('--key', '-k', type=str, action='store', required=True,
                        help='api secret key')
    parser.add_argument('--ldapuser', '-l', type=str, action='store', required=True,
                        help='ldap user name')
    parser.add_argument('--ldappass', '-p', type=str, action='store', required=True,
                        help='ldap password')


    return parser.parse_args()

def run():

    global cert
    global apikey
    global base_url
    global f_src
    global user
    global passw

    args=parse_args()
    config=configurator(args.url, args.key, cert_dir=args.cert_dir, user=args.ldapuser, passw=args.ldappass)
    user=config.get_user()
    passw=config.get_passw()
    cert=config.get_cert()
    apikey=config.get_apikey()
    base_url=config.get_base_url()
    f_src=config.get_fsrc()

    parse_config(domain="main")

if __name__ == "__main__":
    run()
