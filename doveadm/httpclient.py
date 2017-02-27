#!/usr/bin/env python
""" HTTP Client library for Dovecot Doveadm HTTP API.
More details of the API itself can be found from:
http://wiki2.dovecot.org/Design/DoveadmProtocol/HTTP """

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
            73: 'Cannot create file, user out of quota',
            77: 'Authentication failuer',
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

    def run_command(self, command, parameters):
        """ Run command with parameters """
        try:
            req = self.reqs.post(self.apiurl, json=[[command, parameters, "c01"]])
            if req.status_code == 200:
                return req.json()
            return [["error", {"type": "httpError", "httpError": req.status_code}, "c01"]]
        except requests.exceptions.ConnectionError:
            return [["error", {"type": "fatalError"}, "c01"]]
