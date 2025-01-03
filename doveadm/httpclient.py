#!/usr/bin/env python
""" HTTP Client library for Dovecot Doveadm HTTP API. """

from base64 import b64encode
import requests

class DoveAdmHTTPClient(object):
    """ Client for accessing Dovecot Doveadm HTTP API """
    def __init__(self, apiurl, apikey=None, user=None, password=None):
        self.user = user
        self.password = password
        self.apiurl = apiurl
        self.apikey = apikey
        self.commands = {}
        self.errors = {
            64: 'Incorrect parameters',
            65: 'Data error',
            67: 'User does not exist in userdb',
            68: 'Not found',
            73: 'Cannot create file, user out of quota',
            77: 'Authentication failure / permission denied',
            78: 'Invalid configuration'
            }
        self.reqs = requests.Session()
        if self.password:
            self.reqs.auth = (self.user, self.password)
        if self.apikey:
            self.reqs.headers.update({'Authorization': 'X-Dovecot-API '+ b64encode(self.apikey)})

    def get_commands(self):
        """ Retrieve list of available commands and their parameters from API """
        try:
            req = self.reqs.get(self.apiurl)
        except requests.exceptions.ConnectionError:
            return [["error", {"type": "connectionError"}, "c01"]]

        if req.status_code == 200:
            commands = req.json()
            for command in commands:
                self.commands[command['command']] = {}
                for param in command['parameters']:
                    self.commands[command['command']][param['name']] = param['type']
            return req.json()
        else:
            return [["error", {"type": "httpError", "httpError": req.status_code}, "c01"]]

    def generate_curl(self, command, parameters):
        """ Return curl syntax for request. """
        import json
        curl_string = 'curl -H "Authorization: '
        if self.password:
            curl_string += 'Basic %s"' % b64encode('doveadm:' + self.password)
        elif self.apikey:
            curl_string += 'X-Dovecot-API %s"' % b64encode(self.apikey)
        curl_string += ' -H "Content-Type: application/json"'
        curl_string += " -d '%s'" % json.dumps([[command, parameters, "c01"]])
        curl_string += " %s" % self.apiurl
        return curl_string

    def run_command(self, command, parameters):
        """ Run command with parameters """
        try:
            req = self.reqs.post(self.apiurl, json=[[command, parameters, "c01"]])
            if req.status_code == 200:
                return req.json()
            return [["error", {"type": "httpError", "httpError": req.status_code}, "c01"]]
        except requests.exceptions.ConnectionError:
            return [["error", {"type": "fatalError"}, "c01"]]
