import logging
import memcache
import tornado.ioloop
import tornado.web
import tornado.auth
import tornado.gen
from threadutils.handlers import SessionHandler

log = logging.getLogger('handlers.home')
mc = memcache.Client(['127.0.0.1:11211'], debug=1)

class BaseHandler(SessionHandler):

    def get_session(self, id):
        s = mc.get(id)
        return mc.get(id)

    def save_session(self, id, session):
        mc.set(id, session)

    def delete_session(self, id):
        mc.delete(id)

class HomeHandler(BaseHandler):
    def get(self):
        self.render('index.html', foo="bar")

class LoginHandler(BaseHandler, tornado.auth.TwitterMixin):
    @tornado.gen.coroutine
    def get(self):
        yield self.oauth_login(oauth_callback_url='http://localhost:9000/login', redirect_url='/')

class LogoutHandler(BaseHandler):
    def get(self):
        self.logout(redirect_url='/')

class ProtectedHandler(BaseHandler, tornado.auth.TwitterMixin):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        self.render('protected.html')
