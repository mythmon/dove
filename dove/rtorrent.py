import shlex
import socket
from subprocess import Popen, PIPE
from time import sleep

from rtorrent_xmlrpc import SCGIServerProxy

from dove.config import config


class TimeoutException(Exception):
    pass


class ConnectionManager(object):

    def __init__(self):
        self.ssh_tunnel = None
        self.xmlrpc = None

    def connect(self):
        ssh_command = shlex.split((
                'ssh -NL {forward_port}:{rpc_host}:{rpc_port} '
                '-p {ssh_port} {ssh_user}@{ssh_host}')
            .format(**config))

        self.ssh_tunnel = Popen(ssh_command, stdout=PIPE, stdin=PIPE,
                                stderr=PIPE)
        self.xmlrpc = SCGIServerProxy('scgi://localhost:{forward_port}'
                                      .format(**config))

        # Wait for ssh tunnel to be open
        for i in range(config['tunnel_timeout']):
            try:
                self.xmlrpc.system.client_version()
                break
            except socket.error:
                sleep(1)
        else:
            raise TimeoutException('Timed out after {tunnel_timeout} seconds'
                                   .format(**config))

    def disconnect(self):
        self.ssh_tunnel.terminate()

    def __enter__(self):
        try:
            self.connect()
        except TimeoutException:
            self.disconnect()
            raise
        return self.xmlrpc

    def __exit__(self, *exc_info):
        self.disconnect()
