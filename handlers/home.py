import logging
import tornado.ioloop
import tornado.web
import tornado.auth
import tornado.gen

from threadstore.client import ThreadStoreClient

log = logging.getLogger('handlers.home')

class BaseHandler(tornado.web.RequestHandler):
    "base threadreader request handler"

    pass

class HomeHandler(BaseHandler):
    def get(self):
        tag_dir = ThreadStoreClient.instance().blocking_threadstore.posts_tag_directory('threadreader')
        self.render('index.html', foo=str(tag_dir))

