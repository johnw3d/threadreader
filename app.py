#  app.py  - threadreader app main
#
# Copyright (c) John Wainwright 2014 - All rights reserved.
#
__author__ = 'johnw'

import os, sys
import logging
import tornado.ioloop
import tornado.web

import settings
from handlers.home import HomeHandler
from threadstore.client import ThreadStoreClient

handlers = [
    (r"/", HomeHandler),
]

# create main app & threadstore-client singletons
application = tornado.web.Application(handlers, **settings.TORNADO)
threadstore_client = ThreadStoreClient(**settings.THREADSTORE)

logging.basicConfig(filename=os.path.join(settings.LOGS.LOG_ROOT, 'app.log'), filemode='a',
                    level=settings.LOGS.LOG_LEVEL, format=settings.LOGS.LOG_FORMAT)

log = logging.getLogger('app')

def main(argv):
    "threader main, start threadreader webapp"
    # open threadstore client
    threadstore_client.open()
    # start threadreader webapp
    msg = 'Starting Threadreader on port %d...' % settings.APP.port
    log.info(msg)
    print(msg)
    application.listen(settings.APP.port)
    tornado.ioloop.IOLoop.instance().start()

def init_reader_threadstore(argv):
    "init reader threadstore collections"
    threadstore_client.init_reader_threadstore()

def build_test_db(argv):
    "init reader threadstore collections & build test feeds"
    init_reader_threadstore()
    threadstore_client.build_test_db()

# ----------  command-line processor -------

CMDS = {
    "start": main,
    "testdb": build_test_db,
    "cleandb": init_reader_threadstore,
}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = CMDS.get(sys.argv[1])
        if cmd:
            cmd(sys.argv)
        else:
            print(("Unknown command: ", sys.argv[1]))
    else:
        main(sys.argv)
