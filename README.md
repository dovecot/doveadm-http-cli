### Python CLI client for Doveadm HTTP API
doveadm-http-cli is an experimental PoC client for Dovecot doveadm HTTP API written in python. On startup it will connect to the API and fetch all available commands and their accepted parameters. Tab completion is available.

#### Usage
First enable [doveadm HTTP api](https://wiki.dovecot.org/Design/DoveadmProtocol/HTTP)

Then run the client:
```
./doveadm_cli.py --apikey doveadm_apikey --apiurl http://host:port/doveadm/v1
```
or
```
./doveadm_cli.py --password doveadm_password --apiurl http://host:port/doveadm/v1
```

Use tab to expand commands/parameters.

### Advanced
Use command `debug` to enable printing curl commands for API calls

### Example
```
$ ./doveadm_cli.py --apikey someapikey --apiurl http://127.0.0.1:8080/doveadm/v1
=== Doveadm HTTP CLI ===
 - Array type parameters should be comma separated
 - EOF can be specified as a special value for multiline input.
 - Command 'debug' can be used to enable debug printing curl command for each command.
 - 'commands' can be used to display all available commands.
 - Use tab to complete commands/parameters.

(doveadm) debug
Debug set to True
(doveadm) mailboxStatus user=testuser1 mailboxMask=INBOX field=messages

curl -H "Authorization: X-Dovecot-API anV1c3RvNjY2" -H "Content-Type: application/json" -d '[["mailboxStatus", {"field": ["messages"], "mailboxMask": ["INBOX"], "user": "testuser1"}, "c01"]]' http://10.211.55.7:8080/doveadm/v1

[
    {
        "mailbox": "INBOX",
        "messages": "35"
    }
]
Results: 1
```

### TODO
 - Create pypi package.

