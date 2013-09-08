import shlex
import socket
import xmlrpclib
from subprocess import Popen, PIPE
from time import sleep

from dove.config import config


class ConnectionManager(object):

    def __init__(self):
        self.xmlrpc = None

    def connect(self):
        self.xmlrpc = xmlrpclib.ServerProxy(config['rpc_url'])

    def disconnect(self):
        pass

    def __enter__(self):
        self.connect()
        return self.xmlrpc

    def __exit__(self, *exc_info):
        self.disconnect()
