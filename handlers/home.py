import logging
import tornado.ioloop
import tornado.web
import tornado.auth
import tornado.gen

log = logging.getLogger('handlers.home')

class BaseHandler(tornado.web.RequestHandler):
    "base threadreader request handler"

    pass

class HomeHandler(BaseHandler):
    def get(self):
        self.render('index.html', foo="bar")

