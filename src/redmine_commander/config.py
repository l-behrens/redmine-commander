#!/usr/bin/env python
import os
import hashlib
import shelve
import datetime

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

    "main": {
        "options": {
            "Alt+u": ("show my tickets", "parse_config(domain='issues', view='mine')"),
            "Alt+i": ("show open tickets", "parse_config(domain='issues', view='open')"),
            "Alt+o": ("show all tickets", "parse_config(domain='issues', view='all')"),
            "Alt+p": ("show all projects", "parse_config(domain='projects', view='all')"),
            "Alt+r": ("refresh issues", "fetch_all_issues(base_url, apikey, f_src, cert=cert)"),
            "Alt+g": ("refresh projects", "fetch_all_projects(base_url, apikey, f_src, cert=cert)"),
            "Alt+e": ("settings", "parse_config(domain='settings')"),
            "Alt+w": ("show my protocol", "testfunc1()"),
            "Alt+q": ("quit", "testfunc1()"),
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

    def __init__(self, base_url=None, apikey=None, cert_dir=None):
        self.__dict__ = self.__shared_state
        if not self.__register:
            self._init_default_register()
        self._base_url=base_url
        self._apikey=apikey
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

    def get_base_url(self):
        return self._base_url

    def get_apikey(self):
        return self._apikey

    def get_cert(self):
        return self._cert

