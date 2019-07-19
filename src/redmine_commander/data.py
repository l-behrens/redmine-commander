#!/usr/bin/env python
import shelve

def save_settings(base_url, api_token, pem=None, crt=None):
    with shelve.open(conf_file) as f:
        f[base_url]=[api_token, pem, crt]

def load_settings():
    if not os.path.exists(os.path.dirname(conf_file)):
        os.mkdir(os.path.dirname(conf_file))

    # accounts structure
    # {base_url1: [api_token, pem, crt], base_url2: [api_token, pem, crt]}

    with shelve.open(conf_file) as f:
        for k in f.keys():
            yield (k, *f[k])

