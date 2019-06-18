#!/usr/bin/env python
import os
import logging

import requests
from importlib.machinery import SourceFileLoader


class RedmineLib(object):

    _key = ''
    _crt = ''
    _url = ''
    _token = ''

    def __init__(self):
        cnf=os.path.join(os.getenv('HOME'), '.config', 'redmine_commander', 'env.py')
        self._load_config(cnf)

    def _load_config(self, cnf):

        if os.path.exists(cnf):
            try:
                config = SourceFileLoader("config", cnf).load_module()
                self._key=config.key
                self._crt=config.crt
                self._url=config.url
                self._token=config.token
            except Exception as e:
                logging.log(logging.ERROR, 'fucked up: %s' % e)

    def _save_config(self):
        pass

    def _check_config(self):
        pass

    def _request_handler(self, req):
        cert = (self._crt, self._key)
        try:
            if self._crt:
                return requests.get(req, cert=cert)
            else:
                return requests.get(req)
        except Exception as e:
            logging.log(logging.ERROR, "REST Call failed\n%s" %  e)

    def _request_builder(self, r_type, r_obj, *kwargs):
        if r_type is 'GET':
            f_req = '&'.join(['key=%s' % self._token, *kwargs])
            f_req = os.path.join(self._url, "%s?%s" % (r_obj,f_req))
            return f_req


    def fetchMyIssues(self):
        req = self._request_builder("GET",
                                    "issues.json",
                                    "assigned_to_id=me",
                                    "status_id=open",
                                    "limit=500",
                                    "sort=updated_on")
        ret = self._request_handler(req)
        print(ret.text)
        pass

    def fetchAllIssues(self):
        pass

    def getMyIssues(self):
        pass

    def getAllIssues(self):
        pass

if __name__ == "__main__":
    print("fun")
    r=RedmineLib()
    r.fetchMyIssues()
    print(r._url)
    print(r._crt)
    print(r._key)
    print(r._token)

