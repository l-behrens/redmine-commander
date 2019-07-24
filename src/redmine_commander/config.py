#!/usr/bin/env python
import os
import hashlib
import shelve
import datetime

global services
services = [
           "https://gitlab.openinfrastructure.de",
           "https://project.openinfrastructure.de",
           "https://confluence.openinfrastructure.de",
           "https://webmail.openinfrastructure.de",
           "https://app.wire.com"
    ]

global configmap
# template for rofi calls
configmap={
    "settings": {
        "options": {
            "Alt+u": ("new account", "testfunc1()"),
            "Alt+i": ("switch theme", "switch_theme()"),
            "Alt+e": ("edit account", "testfunc1()"),
            "Alt+d": ("delete account", "testfunc1()"),
        },
        "prompt": "testprompt",
        "message": "testmessage",
        "select": "None",
        "generator": "genfunction1()",
        "view":  {
            "default": "{}",
            "all": "get_issues(f_src)"
        }
    },
    "issues": {
        "options": {
            "Alt+o": ("open in browser", "open_in_browser('%s/issues/%s', base_url, t_id)"),
            "Alt+u": ("write a comment", "open_in_browser('%s/issues/%s#', base_url, t_id)"),
            "Alt+r": ("refresh issues", "fetch_all_issues(base_url, apikey, f_src, cert=cert)"),
        },
        "prompt": "issues",
        "message": "list of issues",
        "select": "None",
        "view":  {
            "default": "get_issues(f_src)",
            "all": "get_issues(f_src)",
            "open": "get_issues(f_src, status='New')",
            "mine": "get_issues(f_src, author='Lars Behrens')"
        }
    },
    "projects": {
        "options": {
            "Alt+o": ("open in browser", "open_in_browser('%s/projects/%s', base_url, t_id)"),
            "Alt+r": ("refresh projects", "fetch_all_projects(base_url, apikey, f_src, cert=cert)"),
        },
        "prompt": "issues",
        "message": "list of projects",
        "select": "None",
        "view":  {
            "default": "get_projects(f_src)",
            "all": "get_projects(f_src)",
            "open": "get_projects(f_src, status='New')",
            "mine": "get_projects(f_src, assigned_to='Lars Behrens')"
        }
    },
    "time": {
        "options": {
            "Alt+u": ("show today", "parse_config(domain='time', view='today')"),
            "Alt+i": ("show week", "parse_config(domain='time', view='week')"),
            "Alt+o": ("show month", "parse_config(domain='time', view='month')"),
            "Alt+r": ("refresh", "fetch_all_time(base_url, apikey, f_src, cert=cert)")
        },
        "prompt": "time records",
        "message": "praise the commander!",
        "select": "None",
        "view":  {
            "default": "get_time_entries(f_src, j='', interval='day')",
            "today": "get_time_entries(f_src, j='', interval='day')",
            "week": "get_time_entries(f_src, j='', interval='week')",
            "month": "get_time_entries(f_src, j='', interval='month')"
        }
    },
    "confluence": {
        "options": {
            "Alt+o": ("open in browser", "confluence_open_in_browser(f_src, t_id)"),
            "Alt+p": ("preview", "parse_config(domain='confluence', view='detail', t_id=t_id, on_prev='confluence')"),
            "Alt+r": ("refresh confluence", "fetch_confluence_documents(f_src, cert=cert, user=user, passw=passw)")
        },
        "prompt": "confluence",
        "message": "praise the commander!",
        "select": "None",
        "view":  {
            "default": "get_confluence_documents(f_src)",
            "detail": "preview_document(f_src, t_id)",
            "all": "get_issues()"
        }
    },
    "main": {
        "options": {
            "Alt+x": ("open in browser", "openi_open_in_browser(t_id)"),
            "Alt+u": ("show my tickets", "parse_config(domain='issues', view='mine')"),
            "Alt+i": ("show open tickets", "parse_config(domain='issues', view='open')"),
            "Alt+o": ("show all tickets", "parse_config(domain='issues', view='all')"),
            "Alt+p": ("show all projects", "parse_config(domain='projects', view='all')"),
            "Alt+r": ("refresh issues", "fetch_all_issues(base_url, apikey, f_src, cert=cert)"),
            "Alt+g": ("refresh projects", "fetch_all_projects(base_url, apikey, f_src, cert=cert)"),
            "Alt+h": ("refresh confluence", "fetch_confluence_documents(f_src, cert=cert, user=user, passw=passw)"),
            "Alt+c": ("confluence", "parse_config(domain='confluence')"),
            "Alt+e": ("settings", "parse_config(domain='settings')"),
            "Alt+w": ("show my protocol", "testfunc1()"),
            "Alt+q": ("quit", "sys.exit(1)"),
            "Alt+t": ("time records", "parse_config(domain='time')")
        },
        "prompt": "main",
        "message": "praise the commander!",
        "select": "None",
        "generator": "greeting()",
        "view":  {
            "default": "greeting()",
            "all": "get_issues()"
        }
    }
}


class configurator():
    __shared_state = {}
    # init internal state variables here
    __register = {}

    def __init__(self, base_url=None, apikey=None, cert_dir=None, user=None, passw=None):
        self.__dict__ = self.__shared_state
        if not self.__register:
            self._init_default_register()
        self._base_url=base_url
        self._apikey=apikey
        self._user=user
        self._passw=passw
        self._cert_dir=cert_dir
        self.build()
        pass

    def _init_default_register(self):
        pass

    def build(self):
        if not self._cert_dir is None:
            self._cert=(
                os.path.join(self._cert_dir, 'cert.crt'),
                os.path.join(self._cert_dir, 'key.pem'))

        base_url_sha224=hashlib.sha224(self._base_url.encode('utf-8'))
        self._f_src='/'.join(['/tmp', '%s-issues.db' % base_url_sha224.hexdigest()])
        apikey=self._apikey

    def get_fsrc(self):
        return self._f_src

    def get_passw(self):
        return self._passw

    def get_user(self):
        return self._user

    def get_base_url(self):
        return self._base_url

    def get_apikey(self):
        return self._apikey

    def get_cert(self):
        return self._cert

