import json
import sys

config = {
    'db_url': 'sqlite:///dove.db',
    'rpc_url': 'http://localhost:80/',
    'rsync_port': 22,
    'rsync_opts': '-Phaz',
    'download_dir': 'downloads',
    'parallel': 2,
}

try:
    with open('config.json') as f:
        config.update(json.load(f))
except IOError as e:
    print('Could not open config.json')
    print(e)

required_keys = [
    'db_url',
    'rpc_url',
    'download_dir',
    'rsync_host',
    'rsync_port',
    'rsync_user',
]

fail = False
for key in required_keys:
    if key not in config:
        print('Required config option {key} missing!'.format(key=key))
        fail = True
if fail:
    sys.exit(1)
