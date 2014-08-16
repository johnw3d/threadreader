import os
import logging
import tornado.ioloop
import tornado.web
from handlers.home import HomeHandler

settings = dict(
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    twitter_consumer_key = 'jHkeUDDo4iOy3EE0pUtJgTu1z',
    twitter_consumer_secret = 'qIAIWQmO0ij7mAhm2QEfVRol9SfPbn8X86jlW2Jdd7qIggkBhA',
    cookie_secret = "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
    login_url = "/login",
    debug = True,
    serve_traceback = True,
    xsrf_cookies = True,
)

handlers = [
    (r"/", HomeHandler),
]

application = tornado.web.Application(handlers, **settings)

LOG_ROOT = os.environ.get('THREADREADER_LOG_ROOT', '/var/log/threadreader')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'null': {
            'level': 'DEBUG',
            'class':'django.utils.log.NullHandler',
        },

    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s %(process)d %(filename)s(%(lineno)d): %(levelname)s %(message)s'

logging.basicConfig(filename=os.path.join(LOG_ROOT, 'app.log'), filemode='a', level=LOG_LEVEL, format=LOG_FORMAT)

log = logging.getLogger('views.export')

if __name__ == "__main__":
    log.info('Starting Threadreader on port 9001...')
    print('Starting Threadreader on port 9001...')
    application.listen(9001)
    tornado.ioloop.IOLoop.instance().start()