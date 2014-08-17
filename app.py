#  app.py  - threadreader app main
#
# Copyright (c) John Wainwright 2014 - All rights reserved.
#
__author__ = 'johnw'

import os
import logging
import tornado.ioloop
import tornado.web

import settings
from handlers.home import HomeHandler
from threadstore.client import ThreadStoreClient

handlers = [
    (r"/", HomeHandler),
]

application = tornado.web.Application(handlers, **settings.APP.tornado_settings)

logging.basicConfig(filename=os.path.join(settings.LOGS.LOG_ROOT, 'app.log'), filemode='a',
                    level=settings.LOGS.LOG_LEVEL, format=settings.LOGS.LOG_FORMAT)

log = logging.getLogger('views.export')

if __name__ == "__main__":
    # open threadstore client
    ThreadStoreClient.initialize(settings.THREADSTORE.host,
                                 settings.THREADSTORE.port,
                                 settings.THREADSTORE.client_settings,
                                 settings.THREADSTORE.request_settings)
    # start threadreader webapp
    log.info('Starting Threadreader on port 9001...')
    print('Starting Threadreader on port 9001...')
    application.listen(settings.APP.port)
    tornado.ioloop.IOLoop.instance().start()