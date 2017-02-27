#!/usr/bin/env python

import cmd
import json
import shlex

# Hack for macOS readline
import readline
import rlcompleter
from doveadm.httpclient import DoveAdmHTTPClient

if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")

class DoveAdmCli(cmd.Cmd):
    """ Doveadm Cli """
    prompt = "(doveadm) "

    def add_doveadm_http_api(self, apiurl, apikey=None, user=None, password=None):
        """ Set Doveadm HTTP API credentials and retrieve available commands. """
        self.apiurl = apiurl
        self.user = user
        self.password = password
        self.doveadm = DoveAdmHTTPClient(apiurl=apiurl, apikey=apikey, user=user, password=password)
        response = self.doveadm.get_commands()
        try:
            if response[0][0] == "error":
                if response[0][1]['type'] == 'httpError':
                    return response[0][1]['httpError']
                elif response[0][1]['type'] == 'connectionError':
                    return 1
        except KeyError:
            pass
        return 0

    def do_commands(self, line):
        """ Show available commands or give specific command for parameters """
        line = filter(None, line.split(" "))
        if len(line) == 0:
            for command in self.doveadm.commands:
                print command + ":"
                for param, paramtype in self.doveadm.commands[command].items():
                    print " - name: %s (%s) " % (param, paramtype)
                print
        else:
            self.print_command_params(line[0])

    def print_command_params(self, command):
        """ Print parameters for a command. """
        if command in self.doveadm.commands:
            print "valid parameters for %s: " % command
            for param, paramtype in self.doveadm.commands[command].items():
                print " - %s (%s)" % (param, paramtype)
        else:
            print "invalid command %s" % command

    def read_param_value(self, value, terminator="EOF"):
        """ In case multi line input is required, read all input until terminator. """
        if value == terminator:
            print "Enter multiline input terminated by EOF:"
            value = "\n".join(iter(raw_input, terminator))
        return value

    def completenames(self, text, *ignored):
        """ Override Cmd.completenames to add Doveadm HTTP API commands. """
        names = self.get_names()
        for command in self.doveadm.commands:
            names.append("do_" + command)
        dotext = 'do_'+text
        ret = [a[3:] + " " for a in names if a.startswith(dotext)]
        return ret

    def completedefault(self, text, line, begidx, endidx):
        """ Override Cmd.completedefault to include Doveadm HTTP API Commands and Parameters. """
        if not text:
            completions = [x + "=" for x in self.doveadm.commands[shlex.split(line)[0]]]
        else:
            completions = [f + "=" for f in self.doveadm.commands[shlex.split(line)[0]] if f.startswith(text)]
        return completions

    def preloop(self):
        print "=== Doveadm HTTP CLI ==="
        print " - Array type parameters should be comma separated"
        print " - EOF can be specified as a special value for multiline input."
        print

    def postloop(self):
        """ Exit a bit more nicely. """
        print
        print "Bye!"

    def emptyline(self):
        """ Override Cmd.emptyline not to repeat previous command on empty lines. """
        pass

    def read_response(self, command, response):
        """ Read Doveadm HTTP API response and print output/error. """
        if response:
            if response[0][0] == "error":
                if response[0][1]['type'] == 'exitCode':
                    exit_code = response[0][1]['exitCode']
                    if exit_code in self.doveadm.errors:
                        print self.doveadm.errors[exit_code] + " (exitCode: " + str(exit_code) + ")"
                        if exit_code == 64:
                            self.print_command_params(command)
                    else:
                        print "Unknown error occurred"
                elif response[0][1]['type'] == 'httpError':
                    print "HTTP Error code: " + response[0][1]['httpError']
                elif response[0][1]['type'] == 'fatalError':
                    print "API call failed, invalid parameters?"
            else:
                print json.dumps(response[0][1], indent=4, sort_keys=True)

    def default(self, line):
        """ Override Cmd.default to handle Doveadm HTTP API commands. """
        line = shlex.split(line)
        if line[0] in self.doveadm.commands:
            params = {}
            for param in line[1:]:
                try:
                    param = param.split("=", 1)
                    if param[0] not in self.doveadm.commands[line[0]]:
                        print "invalid parameter: %s" % param[0]
                        self.print_command_params(line[0])
                        return
                    else:
                        if self.doveadm.commands[line[0]][param[0]] == "array":
                            params[param[0]] = param[1].split(",")
                        else:
                            params[param[0]] = self.read_param_value(param[1])
                except:
                    print "Syntax error"

            if len(params) > 0 or len(line) == 1:
                response = self.doveadm.post(command=line[0], parameters=params)
                self.read_response(command=line[0], response=response)

        else:
            print "command not found: " + line[0]

    def do_EOF(self, line):
        """ Handle ^D / EOF to exit. """
        return True

