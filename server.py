#!/usr/bin/env python
import tornado.ioloop
import tornado.web
from tornado.web import HTTPError
from tornado import gen
from tornado.template import Template

import argparse
import base64
import collections
import csv
import hmac
import itertools
import json
import logging
import os
import pipes
import re
import time
import urllib

from scope import Scope, ScopeError, OperationTimeoutError

logger = logging.getLogger(__name__)

g_scope = None

class ScopeImageHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        byts = g_scope.get_screen_image()

        self.set_header('Content-type', 'image/bmp')
        self.write(byts)

class ScopeConnectHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('true' if g_scope is not None else 'false')

    def post(self):
        ip = self.get_argument('ip')
        port = int(self.get_argument('port'))
        global g_scope
        if g_scope is not None:
            try:
                g_scope.shutdown()
            except Exception:
                pass
        g_scope = Scope(ip, port)
        g_scope.connect()
        self.write(g_scope.idn())

class ScopeCmdHandler(tornado.web.RequestHandler):
    def post(self):
        cmd = self.get_argument('cmd')
        expect_output = self.get_argument('expect_output') == 'true'
        self.set_header('Content-type', 'text/plain')
        logger.info("Sending cmd: %s", cmd)
        try:
            res = g_scope._send_command(cmd, check_complete=True, expect_output=expect_output)
        except OperationTimeoutError:
            self.write("Operation timed out")
        else:
            logger.info("Got response: %s", res if len(res) < 500 else (str(len(res)) + ' bytes'))
            self.write(res)

def make_app():
    return tornado.web.Application([
        (r"/cmd", ScopeCmdHandler),
        (r"/screen", ScopeImageHandler),
        (r"/connect", ScopeConnectHandler),
        (r"/(|connect)", tornado.web.StaticFileHandler, {"path": '.', "default_filename": "index.html"}),
    ], autoreload=True)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Run the Tornado server")
    parser.add_argument('start_port', default=8000, type=int, nargs='?',
                        help="What port should we start on? (default 8000)")
    parser.add_argument('offset_port', default=0, type=int, nargs='?',
                        help="Add this number to the port number (optional)")
    args = parser.parse_args()

    port = args.start_port + args.offset_port
    logger.info("Starting Tornado on port %s", port)

    app = make_app()
    app.listen(port, address='127.0.0.1')
    tornado.ioloop.IOLoop.current().start()
