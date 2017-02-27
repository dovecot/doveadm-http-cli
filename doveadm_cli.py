#!/usr/bin/env python

import optparse
from doveadm.cli import DoveAdmCli

def run_cli():
    """ Read command line arguments and run CLI. """
    parser = optparse.OptionParser()
    parser.add_option('-u', '--user', dest='user', help='Doveadm API username', type=str, default='doveadm')
    parser.add_option('-p', '--password', dest='password', help='Doveadm API password', type=str)
    parser.add_option('-k', '--apikey', dest='apikey', help='Dovead API Key', type=str)
    parser.add_option('-a', '--apiurl', dest='apiurl', help='Doveadm API URL', type=str)

    (options, args) = parser.parse_args()
    if not options.user:
        user = 'doveadm'
    else:
        user = options.user

    if not (options.password or options.apikey):
        parser.print_help()
        parser.error('Password or API key not given')

    if not options.apiurl:
        parser.print_help()
        parser.error('Doveadm API URL not given')

    doveadmcli = DoveAdmCli()
    doveadmcli.add_doveadm_http_api(apiurl=options.apiurl, apikey=options.apikey, user=user, password=options.password)
    doveadmcli.cmdloop()

if __name__ == '__main__':
    run_cli()
