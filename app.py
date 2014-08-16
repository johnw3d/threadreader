#  app.py  - threadreader app main
#
# Copyright (c) John Wainwright 2014 - All rights reserved.
#
__author__ = 'johnw'

import os
import logging
import tornado.ioloop
import tornado.web

from threadclient.tornado_client import AsyncThreadStore

from handlers.home import HomeHandler
import settings

threadstore = None

handlers = [
    (r"/", HomeHandler),
]

application = tornado.web.Application(handlers, **settings.APP['settings'])

logging.basicConfig(filename=os.path.join(settings.LOGS['LOG_ROOT'], 'app.log'), filemode='a',
                    level=settings.LOGS['LOG_LEVEL'], format=settings.LOGS['LOG_FORMAT'])

log = logging.getLogger('views.export')

if __name__ == "__main__":
    # open threadstore client
    global threadstore
    threadstore = AsyncThreadStore()
    # start threadreader webapp
    log.info('Starting Threadreader on port 9001...')
    print('Starting Threadreader on port 9001...')
    application.listen(settings.APP['port'])
    tornado.ioloop.IOLoop.instance().start()