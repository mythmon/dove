import json
import sys

config = {
    'db_url': 'sqlite:///dove.db',
    'ssh_port': 22,
    'tunnel_timeout': 10,
    'forward_port': 51015,
    'rpc_host': 'localhost',
}

try:
    with open('config.json') as f:
        config.update(json.load(f))
except IOError as e:
    print('Could not open config.json')
    print(e)

required_keys = [
    'db_url',
    'ssh_port', 'ssh_user', 'ssh_host',
    'forward_port', 'tunnel_timeout',
    'rpc_host', 'rpc_port',
]

fail = False
for key in required_keys:
    if key not in config:
        print('Required config option {key} missing!'.format(key=key))
        fail = True
if fail:
    sys.exit(1)
